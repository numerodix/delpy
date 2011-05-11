unit SocketClient;

interface

uses
  SysUtils, Classes, Variants, Windows, Forms,
  SocketTypes;

function OpenRead: TMemoryStream;
procedure CloseRead(memstr: TMemoryStream);
function OpenWrite(funcname: string): TMemoryStream;
procedure CloseWrite(funcname: string; memstr: TMemoryStream);

procedure Receive(
    args: array of Pointer;
    types: array of TTransmissionType);
procedure Transmit(cmd: string;
    args: array of Pointer;
    lengths: array of integer;
    types: array of TTransmissionType); overload;
procedure Transmit(cmd: string); overload;

procedure Connect;
procedure Disconnect;


implementation

uses
  IdTCPClient, IdTCPConnection,
  SocketInfo, SocketMarshall;

type
  TConnectionHandler = class(TObject)
    public
      procedure HandleConnected(Sender: TObject);
      procedure HandleDisconnected(Sender: TObject);
  end;

var
  TCPClient: TIdTCPClient;
  ConnectionHandler: TConnectionHandler;
  Link: TIdTCPConnection;
  CallSerialNumber: integer = 1;


function OpenRead: TMemoryStream;
var
  callid: SocketTypes.TCallId;
  timestamp: Int64;
begin
  Application.ProcessMessages;

  Connect;

  Result := SocketMarshall.OpenRead(Link);
  callid := SocketTypes.TCallId.Create;
  try
    SocketMarshall.ReadHeader(Result, callid, @timestamp);
    SocketTypes.WriteReceived(SocketTypes.eventReturn, SocketTypes.hostClient,
        callid, Result.Size, Windows.GetTickCount - timestamp);
  finally
    callid.Free;
  end;
end;

procedure CloseRead(memstr: TMemoryStream);
begin
  SocketMarshall.CloseRead(Link, memstr);
end;

function OpenWrite(funcname: string): TMemoryStream;
var
  callid: SocketTypes.TCallId;
begin
  Application.ProcessMessages;

  Connect;

  Result := SocketMarshall.OpenWrite(Link);
  callid := SocketTypes.TCallId.Create(funcname, CallSerialNumber);
  try
    SocketMarshall.WriteHeader(Result, callid);
  finally
    callid.Free;
  end;
end;

procedure CloseWrite(funcname: string; memstr: TMemoryStream);
var
  callid: SocketTypes.TCallId;
begin
  callid := SocketTypes.TCallId.Create(funcname, CallSerialNumber);
  try
    SocketTypes.WriteTransmit(SocketTypes.eventCall, SocketTypes.hostClient,
        callid, memstr.Size);
    SocketTypes.FakeLatency(memstr.Size);
  finally
    CallSerialNumber := CallSerialNumber + 1;
    callid.Free;
    SocketMarshall.CloseWrite(Link, memstr);
  end;
end;


procedure Receive(
    args: array of Pointer;
    types: array of TTransmissionType);
var
  memstr: TMemoryStream;
begin
  memstr := OpenRead;
  SocketMarshall.Read(memstr, args, types);
  CloseRead(memstr);
end;

procedure Transmit(cmd: string;
    args: array of Pointer;
    lengths: array of integer;
    types: array of TTransmissionType);
var
  memstr: TMemoryStream;
begin
  memstr := OpenWrite(cmd);
  SocketMarshall.Write(memstr, args, lengths, types);
  CloseWrite(cmd, memstr);
end;

procedure Transmit(cmd: string);
begin
  Transmit(cmd, [], [], []);
end;


procedure TConnectionHandler.HandleConnected(Sender: TObject);
begin
  System.WriteLn('(c) Client connected');
  Link := TCPClient;
end;

procedure TConnectionHandler.HandleDisconnected(Sender: TObject);
begin
  System.WriteLn('(c) Client disconnected');
  Link := Nil;
end;


procedure Connect;
begin
  if ConnectionHandler = Nil then
    ConnectionHandler := TConnectionHandler.Create;

  if TCPClient = Nil then
    begin
      TCPClient := TIdTCPClient.Create(Nil);
      TCPClient.OnConnected := ConnectionHandler.HandleConnected;
      TCPClient.OnDisconnected := ConnectionHandler.HandleDisconnected;
    end;


  if not TCPClient.Connected then
    try
      TCPClient.Host := SocketConnectionIp;
      TCPClient.Port := SocketConnectionPort;
      TCPClient.Connect;
    except on E:Exception do
      System.WriteLn(E.Message);
    end;
end;

procedure Disconnect;
begin
  if TCPClient.Connected then
    TCPClient.Disconnect;
end;

end.
