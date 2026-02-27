.PHONY: proto proto-go proto-python test test-go test-python clean

proto: proto-go proto-python

proto-go:
	protoc \
		--go_out=cli/gen/denden --go_opt=paths=source_relative \
		--go-grpc_out=cli/gen/denden --go-grpc_opt=paths=source_relative \
		-I proto \
		proto/denden.proto

proto-python:
	python -m grpc_tools.protoc \
		--python_out=server/src/denden/gen \
		--grpc_python_out=server/src/denden/gen \
		--pyi_out=server/src/denden/gen \
		-I proto \
		proto/denden.proto
	@# Fix generated imports to work inside the denden.gen package
	sed 's/^import denden_pb2/from denden.gen import denden_pb2/' \
		server/src/denden/gen/denden_pb2_grpc.py > server/src/denden/gen/denden_pb2_grpc.py.tmp && \
		mv server/src/denden/gen/denden_pb2_grpc.py.tmp server/src/denden/gen/denden_pb2_grpc.py

test: test-go test-python

test-go:
	cd cli && go test -v -timeout 60s ./...

test-python:
	cd server && python -m pytest tests/ -v

clean:
	rm -f cli/gen/denden/*.go
	rm -f server/src/denden/gen/denden_pb2*.py*
