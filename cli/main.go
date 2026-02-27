package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/google/uuid"
	pb "github.com/strawpot/denden/cli/gen/denden"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/types/known/timestamppb"
)

const version = "1.0"

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	switch os.Args[1] {
	case "send":
		handleSend()
	case "status":
		handleStatus()
	case "--help", "-h", "help":
		printUsage()
	default:
		fmt.Fprintf(os.Stderr, "unknown command: %s\n", os.Args[1])
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Fprintln(os.Stderr, `usage: denden <command> [args]

commands:
  send   <json>   Send a DenDenRequest (auto-fills request_id, version, trace, timestamp)
  status          Check orchestrator health

environment:
  DENDEN_ADDR              server address (default: 127.0.0.1:9700)
  DENDEN_AGENT_ID          this agent's instance ID (auto-set by orchestrator)
  DENDEN_PARENT_AGENT_ID   parent agent's instance ID
  DENDEN_WORKTREE_ID       worktree ID
  DENDEN_TIMEOUT           request timeout e.g. "30s" (default: 30s)`)
}

// handleSend parses raw JSON, auto-fills envelope fields, sends via gRPC.
func handleSend() {
	if len(os.Args) < 3 {
		fmt.Fprintln(os.Stderr, "usage: denden send '<json>'")
		os.Exit(1)
	}

	rawJSON := os.Args[2]

	// Parse the raw JSON into a protobuf message.
	req := &pb.DenDenRequest{}
	unmarshaler := protojson.UnmarshalOptions{DiscardUnknown: true}
	if err := unmarshaler.Unmarshal([]byte(rawJSON), req); err != nil {
		fmt.Fprintf(os.Stderr, "invalid JSON: %v\n", err)
		os.Exit(1)
	}

	// Auto-fill envelope fields if not provided.
	if req.DendenVersion == "" {
		req.DendenVersion = version
	}
	if req.RequestId == "" {
		req.RequestId = "req_" + uuid.New().String()
	}
	if req.Trace == nil {
		req.Trace = &pb.Trace{}
	}
	if req.Trace.CreatedAt == nil {
		req.Trace.CreatedAt = timestamppb.Now()
	}
	if req.Trace.AgentInstanceId == "" {
		req.Trace.AgentInstanceId = os.Getenv("DENDEN_AGENT_ID")
	}
	if req.Trace.ParentAgentInstanceId == "" {
		req.Trace.ParentAgentInstanceId = os.Getenv("DENDEN_PARENT_AGENT_ID")
	}
	if req.Trace.WorktreeId == "" {
		req.Trace.WorktreeId = os.Getenv("DENDEN_WORKTREE_ID")
	}

	// Validate that a payload is set (oneof).
	if req.GetAskUser() == nil && req.GetDelegate() == nil {
		fmt.Fprintln(os.Stderr, "error: either 'askUser' or 'delegate' payload is required")
		os.Exit(1)
	}

	// Send via gRPC.
	conn, ctx, cancel := dial()
	defer conn.Close()
	defer cancel()

	client := pb.NewDendenClient(conn)
	resp, err := client.Send(ctx, req)
	if err != nil {
		printGRPCError(err)
		os.Exit(1)
	}

	// Output response as JSON.
	marshaler := protojson.MarshalOptions{
		Multiline:       true,
		Indent:          "  ",
		EmitUnpopulated: false,
	}
	out, err := marshaler.Marshal(resp)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error marshaling response: %v\n", err)
		os.Exit(1)
	}
	fmt.Println(string(out))

	// Exit non-zero on error/denied status.
	if resp.Status == pb.ResponseStatus_ERROR || resp.Status == pb.ResponseStatus_DENIED {
		os.Exit(1)
	}
}

func handleStatus() {
	conn, ctx, cancel := dial()
	defer conn.Close()
	defer cancel()

	client := pb.NewDendenClient(conn)
	resp, err := client.Status(ctx, &pb.StatusRequest{})
	if err != nil {
		printGRPCError(err)
		os.Exit(1)
	}

	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	enc.Encode(map[string]any{
		"uptime_seconds": resp.UptimeSeconds,
		"active_agents":  resp.ActiveAgents,
	})
}

func dial() (*grpc.ClientConn, context.Context, context.CancelFunc) {
	addr := os.Getenv("DENDEN_ADDR")
	if addr == "" {
		addr = "127.0.0.1:9700"
	}

	timeout := 30 * time.Second
	if t := os.Getenv("DENDEN_TIMEOUT"); t != "" {
		if d, err := time.ParseDuration(t); err == nil {
			timeout = d
		}
	}

	ctx, cancel := context.WithTimeout(context.Background(), timeout)

	conn, err := grpc.NewClient(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		fmt.Fprintf(os.Stderr, "connection failed: %v\n", err)
		os.Exit(1)
	}

	return conn, ctx, cancel
}

func printGRPCError(err error) {
	if st, ok := status.FromError(err); ok {
		fmt.Fprintf(os.Stderr, "error: %s: %s\n", st.Code(), st.Message())
	} else {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
	}
}
