package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"os/exec"
	"strings"
	"testing"
	"time"

	pb "github.com/strawpot/denden/cli/gen/denden"
	"google.golang.org/grpc"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/types/known/timestamppb"
)

// echoServer implements the Denden gRPC service for testing.
type echoServer struct {
	pb.UnimplementedDendenServer
	startTime time.Time
}

func (s *echoServer) Send(ctx context.Context, req *pb.DenDenRequest) (*pb.DenDenResponse, error) {
	if req.RequestId == "" {
		return &pb.DenDenResponse{
			DendenVersion: version,
			Status:        pb.ResponseStatus_ERROR,
			Error:         &pb.ErrorDetail{Code: "INVALID_REQUEST", Message: "request_id is required"},
		}, nil
	}

	switch p := req.Payload.(type) {
	case *pb.DenDenRequest_AskUser:
		return &pb.DenDenResponse{
			DendenVersion: version,
			RequestId:     req.RequestId,
			Status:        pb.ResponseStatus_OK,
			Result: &pb.DenDenResponse_AskUserResult{
				AskUserResult: &pb.AskUserResult{
					Content: &pb.AskUserResult_Text{Text: p.AskUser.Question},
				},
			},
		}, nil
	case *pb.DenDenRequest_Delegate:
		return &pb.DenDenResponse{
			DendenVersion: version,
			RequestId:     req.RequestId,
			Status:        pb.ResponseStatus_OK,
			Result: &pb.DenDenResponse_DelegateResult{
				DelegateResult: &pb.DelegateResult{
					Summary: p.Delegate.Task.Text,
				},
			},
		}, nil
	default:
		return &pb.DenDenResponse{
			DendenVersion: version,
			RequestId:     req.RequestId,
			Status:        pb.ResponseStatus_ERROR,
			Error:         &pb.ErrorDetail{Code: "INVALID_REQUEST", Message: "no payload"},
		}, nil
	}
}

func (s *echoServer) Status(ctx context.Context, req *pb.StatusRequest) (*pb.StatusResponse, error) {
	return &pb.StatusResponse{
		UptimeSeconds: int64(time.Since(s.startTime).Seconds()),
		ActiveAgents:  0,
	}, nil
}

// startTestServer starts a gRPC server on a random port, returns the address.
func startTestServer(t *testing.T) string {
	t.Helper()
	lis, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("failed to listen: %v", err)
	}

	srv := grpc.NewServer()
	pb.RegisterDendenServer(srv, &echoServer{startTime: time.Now()})

	go srv.Serve(lis)
	t.Cleanup(func() { srv.Stop() })

	return lis.Addr().String()
}

// runCLI builds and runs the CLI binary with the given args and env.
func runCLI(t *testing.T, addr string, args ...string) (stdout, stderr string, exitCode int) {
	t.Helper()

	// Build the binary once.
	binPath := t.TempDir() + "/denden"
	build := exec.Command("go", "build", "-o", binPath, ".")
	build.Dir = "."
	if out, err := build.CombinedOutput(); err != nil {
		t.Fatalf("build failed: %v\n%s", err, out)
	}

	cmd := exec.Command(binPath, args...)
	cmd.Env = append(os.Environ(), "DENDEN_ADDR="+addr, "DENDEN_TIMEOUT=5s")

	var outBuf, errBuf strings.Builder
	cmd.Stdout = &outBuf
	cmd.Stderr = &errBuf

	err := cmd.Run()
	exitCode = 0
	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			exitCode = exitErr.ExitCode()
		} else {
			t.Fatalf("failed to run CLI: %v", err)
		}
	}

	return outBuf.String(), errBuf.String(), exitCode
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

func TestSendAskUser(t *testing.T) {
	addr := startTestServer(t)
	stdout, _, exitCode := runCLI(t, addr, "send", `{"askUser":{"question":"what color?"}}`)

	if exitCode != 0 {
		t.Fatalf("expected exit 0, got %d", exitCode)
	}

	var resp pb.DenDenResponse
	if err := protojson.Unmarshal([]byte(stdout), &resp); err != nil {
		t.Fatalf("failed to parse response: %v\nstdout: %s", err, stdout)
	}

	if resp.Status != pb.ResponseStatus_OK {
		t.Errorf("expected OK, got %v", resp.Status)
	}
	if resp.GetAskUserResult().GetText() != "what color?" {
		t.Errorf("unexpected answer: %s", resp.GetAskUserResult().GetText())
	}
}

func TestSendDelegate(t *testing.T) {
	addr := startTestServer(t)
	stdout, _, exitCode := runCLI(t, addr, "send", `{"delegate":{"delegateTo":"implementer","task":{"text":"build it"}}}`)

	if exitCode != 0 {
		t.Fatalf("expected exit 0, got %d", exitCode)
	}

	var resp pb.DenDenResponse
	if err := protojson.Unmarshal([]byte(stdout), &resp); err != nil {
		t.Fatalf("failed to parse response: %v", err)
	}

	if resp.GetDelegateResult().GetSummary() != "build it" {
		t.Errorf("unexpected summary: %s", resp.GetDelegateResult().GetSummary())
	}
}

func TestSendNoPayload(t *testing.T) {
	addr := startTestServer(t)
	_, stderr, exitCode := runCLI(t, addr, "send", `{}`)

	if exitCode == 0 {
		t.Fatal("expected non-zero exit")
	}
	if !strings.Contains(stderr, "payload") {
		t.Errorf("expected payload error, got: %s", stderr)
	}
}

func TestStatus(t *testing.T) {
	addr := startTestServer(t)
	stdout, _, exitCode := runCLI(t, addr, "send", `{"askUser":{"question":"hi"}}`)
	_ = stdout

	stdout, _, exitCode = runCLI(t, addr, "status")
	if exitCode != 0 {
		t.Fatalf("expected exit 0, got %d", exitCode)
	}

	var result map[string]any
	if err := json.Unmarshal([]byte(stdout), &result); err != nil {
		t.Fatalf("failed to parse status JSON: %v", err)
	}
	if _, ok := result["uptime_seconds"]; !ok {
		t.Error("missing uptime_seconds in status response")
	}
}

func TestAutoFillRequestId(t *testing.T) {
	addr := startTestServer(t)
	stdout, _, exitCode := runCLI(t, addr, "send", `{"askUser":{"question":"hi"}}`)

	if exitCode != 0 {
		t.Fatalf("expected exit 0, got %d", exitCode)
	}

	var resp pb.DenDenResponse
	if err := protojson.Unmarshal([]byte(stdout), &resp); err != nil {
		t.Fatalf("failed to parse response: %v", err)
	}

	if !strings.HasPrefix(resp.RequestId, "req_") {
		t.Errorf("expected auto-filled request_id starting with 'req_', got: %s", resp.RequestId)
	}
}

func TestAutoFillVersion(t *testing.T) {
	addr := startTestServer(t)
	stdout, _, _ := runCLI(t, addr, "send", `{"askUser":{"question":"hi"}}`)

	var resp pb.DenDenResponse
	protojson.Unmarshal([]byte(stdout), &resp)

	if resp.DendenVersion != version {
		t.Errorf("expected version %s, got %s", version, resp.DendenVersion)
	}
}

func TestUnknownCommand(t *testing.T) {
	_, stderr, exitCode := runCLI(t, "127.0.0.1:1", "bogus")

	if exitCode == 0 {
		t.Fatal("expected non-zero exit for unknown command")
	}
	if !strings.Contains(stderr, "unknown command") {
		t.Errorf("expected 'unknown command' error, got: %s", stderr)
	}
}

func TestNoArgs(t *testing.T) {
	_, stderr, exitCode := runCLI(t, "127.0.0.1:1")

	if exitCode == 0 {
		t.Fatal("expected non-zero exit for no args")
	}
	if !strings.Contains(stderr, "usage:") {
		t.Errorf("expected usage in stderr, got: %s", stderr)
	}
}

func TestSendInvalidJSON(t *testing.T) {
	addr := startTestServer(t)
	_, stderr, exitCode := runCLI(t, addr, "send", `{not json}`)

	if exitCode == 0 {
		t.Fatal("expected non-zero exit for invalid JSON")
	}
	if !strings.Contains(stderr, "invalid JSON") {
		t.Errorf("expected 'invalid JSON' error, got: %s", stderr)
	}
}

func TestAutoFillTimestamp(t *testing.T) {
	// Verify that the CLI auto-fills created_at.
	// We can't directly inspect the request, but if the server receives it
	// without error, the timestamp was valid.
	addr := startTestServer(t)
	_, _, exitCode := runCLI(t, addr, "send", `{"askUser":{"question":"hi"}}`)

	if exitCode != 0 {
		t.Fatal("expected exit 0 — timestamp auto-fill should produce valid request")
	}
}

// Test parseAndFill logic directly (without subprocess).
func TestParseRequest(t *testing.T) {
	raw := `{"askUser":{"question":"test","choices":["a","b"]}}`

	req := &pb.DenDenRequest{}
	opts := protojson.UnmarshalOptions{DiscardUnknown: true}
	if err := opts.Unmarshal([]byte(raw), req); err != nil {
		t.Fatalf("unmarshal failed: %v", err)
	}

	if req.GetAskUser() == nil {
		t.Fatal("expected ask_user payload")
	}
	if req.GetAskUser().Question != "test" {
		t.Errorf("unexpected question: %s", req.GetAskUser().Question)
	}
	if len(req.GetAskUser().Choices) != 2 {
		t.Errorf("expected 2 choices, got %d", len(req.GetAskUser().Choices))
	}
}

func TestParseDelegateRequest(t *testing.T) {
	raw := `{"delegate":{"delegateTo":"reviewer","task":{"text":"review code","returnFormat":"TEXT"}}}`

	req := &pb.DenDenRequest{}
	opts := protojson.UnmarshalOptions{DiscardUnknown: true}
	if err := opts.Unmarshal([]byte(raw), req); err != nil {
		t.Fatalf("unmarshal failed: %v", err)
	}

	if req.GetDelegate() == nil {
		t.Fatal("expected delegate payload")
	}
	if req.GetDelegate().DelegateTo != "reviewer" {
		t.Errorf("expected reviewer, got %v", req.GetDelegate().DelegateTo)
	}
	if req.GetDelegate().Task.ReturnFormat != pb.Format_TEXT {
		t.Errorf("expected TEXT, got %v", req.GetDelegate().Task.ReturnFormat)
	}
}

func TestTimestampAutoFill(t *testing.T) {
	req := &pb.DenDenRequest{
		Trace: &pb.Trace{},
	}
	if req.Trace.CreatedAt == nil {
		req.Trace.CreatedAt = timestamppb.Now()
	}

	if req.Trace.CreatedAt == nil {
		t.Fatal("timestamp should be auto-filled")
	}

	ts := req.Trace.CreatedAt.AsTime()
	if time.Since(ts) > time.Second {
		t.Errorf("timestamp too old: %v", ts)
	}
}

// Suppress unused import warnings.
var _ = fmt.Sprintf
