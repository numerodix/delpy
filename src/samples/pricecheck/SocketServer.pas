unit SocketServer;

interface

uses
  SysUtils, Classes, Variants, Windows,
  IdTCPConnection, SocketTypes;

procedure Transmit(const link: TIdTCPConnection;
    const callid: TCallId;
    const instream: TMemoryStream);

procedure StartServer;
procedure StopServer;


implementation

uses
  IdTCPServer, IdSocketHandle,
  SocketInfo, SocketMarshall,
  SocketServiceHandlers;

type
  TConnectionHandler = class(TObject) {dummy class for handler methods}
    public
      procedure HandleClientConnect(AThread: TIdPeerThread);
      procedure HandleClientDisconnect(AThread: TIdPeerThread);
      procedure HandleClientExecute(AThread: TIdPeerThread);
  end;

var
  TCPServer: TIdTCPServer;
  ConnectionHandler: TConnectionHandler;
  Link: TIdTCPConnection;


procedure Transmit(const link: TIdTCPConnection;
    const callid: TCallId;
    const instream: TMemoryStream);
var
  memstr: TMemoryStream;
  headersize, payload: integer;
begin
  memstr := SocketMarshall.OpenWrite(link);
  headersize := -1; payload := -1;

  try
    // write header to measure length
    SocketMarshall.WriteHeader(memstr, callid);
    headersize := memstr.Size;

    SocketServiceHandlers.HandlerIndex.Find(callid.Funcname)(
        instream, memstr);
    payload := memstr.Size;

    if payload > headersize then
      begin
        // write header to send
        memstr.Position := 0;
        SocketMarshall.WriteHeader(memstr, callid);

        SocketTypes.WriteTransmit(SocketTypes.eventReturn, SocketTypes.hostServer,
            callid, memstr.Size);
        SocketTypes.FakeLatency(memstr.Size);
      end;
  finally
    SocketMarshall.CloseWrite(link, memstr, payload = headersize);
  end;
end;

procedure DispatchCall(const link: TIdTCPConnection);
var
  memstr: TMemoryStream;
  callid: SocketTypes.TCallId;
  timestamp: Int64;
begin
  memstr := SocketMarshall.OpenRead(link);
  callid := SocketTypes.TCallId.Create;
  try
    SocketMarshall.ReadHeader(memstr, callid, @timestamp);
    SocketTypes.WriteReceived(SocketTypes.eventCall, SocketTypes.hostServer,
        callid, memstr.Size, Windows.GetTickCount - timestamp);

    Transmit(link, callid, memstr);
  finally
    callid.Free;
    SocketMarshall.CloseRead(link, memstr);
  end;
end;


procedure TConnectionHandler.HandleClientConnect(AThread: TIdPeerThread);
begin
  WriteLn('(s) Client connected');
  Link := AThread.Connection;
end;

procedure TConnectionHandler.HandleClientDisconnect(AThread: TIdPeerThread);
begin
  WriteLn('(s) Client disconnected');
  Link := Nil;
end;

procedure TConnectionHandler.HandleClientExecute(AThread: TIdPeerThread);
begin
  SocketServiceHandlers.InitIndex;
  DispatchCall(Link);
end;


procedure StartServer;
var
  Bindings: TIdSocketHandles;
begin
  if ConnectionHandler = Nil then
    ConnectionHandler := TConnectionHandler.Create;

  if TCPServer = Nil then
    begin
      TCPServer := TIdTCPServer.Create(Nil);
      TCPServer.OnConnect := ConnectionHandler.HandleClientConnect;
      TCPServer.OnDisconnect := ConnectionHandler.HandleClientDisconnect;
      TCPServer.OnExecute := ConnectionHandler.HandleClientExecute;
    end;


  if not TCPServer.Active then
    begin
      Bindings := TIdSocketHandles.Create(TCPServer);
      try
        with Bindings.Add do
          begin
            IP := SocketConnectionIp;
            Port := SocketConnectionPort;
          end;
        try
          TCPServer.Bindings := Bindings;
          TCPServer.Active := True;
        except on E:Exception do
          System.WriteLn(E.Message);
        end;
      finally
        Bindings.Free;
      end;

      if TCPServer.Active then
        System.WriteLn('(s) SocketServer running on '
          + TCPServer.Bindings[0].IP + ':' + IntToStr(TCPServer.Bindings[0].Port));
    end;
end;

procedure StopServer;
begin
  if TCPServer.Active then
    TCPServer.Active := False;

  if not TCPServer.Active then
    System.WriteLn('(s) SocketServer stopped');
end;


end.
