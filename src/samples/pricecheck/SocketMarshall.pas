unit SocketMarshall;

interface

uses
  SysUtils, Classes, Variants, Windows,
  IdTCPConnection,
  SocketTypes;


procedure ReadString(const memstr: TMemoryStream; pstr: Pointer);
procedure WriteString(const memstr: TMemoryStream; pstr: Pointer; len: integer);

procedure ReadFlat(const memstr: TMemoryStream; p: Pointer);
procedure WriteFlat(const memstr: TMemoryStream; p: Pointer; len: integer);

procedure ReadHeader(const memstr: TMemoryStream;
    callid: SocketTypes.TCallId; timestamp: Pointer);
procedure WriteHeader(const memstr: TMemoryStream;
    callid: SocketTypes.TCallId);

procedure Read(const memstr: TMemoryStream;
    args: array of Pointer;
    types: array of TTransmissionType);
procedure Write(const memstr: TMemoryStream;
    args: array of Pointer;
    lengths: array of integer;
    types: array of TTransmissionType);

function OpenRead(const link: TIdTCPConnection): TMemoryStream;
procedure CloseRead(const link: TIdTCPConnection;
    const memstr: TMemoryStream);
function OpenWrite(const link: TIdTCPConnection): TMemoryStream;
procedure CloseWrite(const link: TIdTCPConnection;
    const memstr: TMemoryStream; cancel: boolean = False);

procedure Receive(const link: TIdTCPConnection;
    args: array of Pointer;
    types: array of TTransmissionType);
procedure Transmit(const link: TIdTCPConnection;
    args: array of Pointer;
    lengths: array of integer;
    types: array of TTransmissionType);


implementation

procedure ReadHeader(const memstr: TMemoryStream;
    callid: SocketTypes.TCallId; timestamp: Pointer);
begin
  Read(memstr,
      [@callid.Funcname, @callid.id],
      [SocketTypes.transString, SocketTypes.transFlat]);
  SocketMarshall.ReadFlat(memstr, timestamp);
end;

procedure WriteHeader(const memstr: TMemoryStream;
    callid: SocketTypes.TCallId);
var
  time: Int64;
begin
  Write(memstr,
      [@callid.Funcname, @callid.id],
      [Length(callid.Funcname), SizeOf(callid.id)],
      [SocketTypes.transString, SocketTypes.transFlat]);
  time := Windows.GetTickCount;
  SocketMarshall.WriteFlat(memstr, @time, SizeOf(time));
end;


procedure ReadString(const memstr: TMemoryStream; pstr: Pointer);
var
  len: integer;
begin
  memstr.Read(len, SizeOf(len));
  SetLength(string(pstr^), len);
  memstr.Read(Pointer(string(pstr^))^, len);
end;

procedure WriteString(const memstr: TMemoryStream; pstr: Pointer; len: integer);
begin
  memstr.Write(len, SizeOf(len));
  memstr.Write(Pointer(string(pstr^))^, len);
end;


procedure ReadFlat(const memstr: TMemoryStream; p: Pointer);
var
  len: integer;
begin
  memstr.Read(len, SizeOf(len));
  memstr.Read(p^, len);
end;

procedure WriteFlat(const memstr: TMemoryStream; p: Pointer; len: integer);
begin
  memstr.Write(len, SizeOf(len));
  memstr.Write(p^, len);
end;


procedure Read(const memstr: TMemoryStream;
    args: array of Pointer;
    types: array of TTransmissionType);
var
  i: integer;
begin
  for i := Low(args) to High(args) do
    begin
      if types[i] = transString then
        ReadString(memstr, args[i])
      else
        ReadFlat(memstr, args[i]);
    end;
end;

procedure Write(const memstr: TMemoryStream;
    args: array of Pointer;
    lengths: array of integer;
    types: array of TTransmissionType);
var
  i: integer;
begin
  for i := Low(args) to High(args) do
    begin
      if types[i] = transString then
        WriteString(memstr, args[i], lengths[i])
      else
        WriteFlat(memstr, args[i], lengths[i]);
    end;
end;


function OpenRead(const link: TIdTCPConnection): TMemoryStream;
var
  size: integer;
begin
  Result := TMemoryStream.Create;
  size := link.ReadInteger;
  link.ReadStream(Result, size);
  Result.Position := 0;
end;

procedure CloseRead(const link: TIdTCPConnection;
    const memstr: TMemoryStream);
begin
  memstr.Free;
end;

function OpenWrite(const link: TIdTCPConnection): TMemoryStream;
begin
  Result := TMemoryStream.Create;
end;

procedure CloseWrite(const link: TIdTCPConnection;
    const memstr: TMemoryStream; cancel: boolean = False);
begin
  if not cancel then
    begin
      memstr.Position := 0;
      link.WriteInteger(memstr.Size);
      link.OpenWriteBuffer;
      link.WriteStream(memstr);
      link.CloseWriteBuffer;
    end;
  memstr.Free;
end;


procedure Receive(const link: TIdTCPConnection;
    args: array of Pointer;
    types: array of TTransmissionType);
var
  memstr: TMemoryStream;
begin
  memstr := OpenRead(link);
  try
    Read(memstr, args, types);
  finally
    CloseRead(link, memstr);
  end;
end;

procedure Transmit(const link: TIdTCPConnection;
    args: array of Pointer;
    lengths: array of integer;
    types: array of TTransmissionType);
var
  memstr: TMemoryStream;
begin
  memstr := OpenWrite(link);
  try
    Write(memstr, args, lengths, types);
  finally
    CloseWrite(link, memstr);
  end;
end;

end.
