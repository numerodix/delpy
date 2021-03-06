unit SocketServer;

interface

procedure StartServer;
procedure StopServer;


implementation

uses
  SysUtils, Classes, Variants,
  IdTCPServer, IdSocketHandle, IdTCPConnection,
  SocketInfo;

type
  THandler = class(TObject) {dummy class for handler methods}
    public
      procedure HandleClientConnect(AThread: TIdPeerThread);
      procedure HandleClientDisconnect(AThread: TIdPeerThread);
      procedure HandleClientExecute(AThread: TIdPeerThread);
  end;

var
  TCPServer: TIdTCPServer;
  Handler: THandler;
  Link: TIdTCPConnection;


procedure THandler.HandleClientConnect(AThread: TIdPeerThread);
begin
  WriteLn('(s) Client connected');
  Link := AThread.Connection;
end;

procedure THandler.HandleClientDisconnect(AThread: TIdPeerThread);
begin
  WriteLn('(s) Client disconnected');
  Link := Nil;
end;

procedure THandler.HandleClientExecute(AThread: TIdPeerThread);
var
  X, Y: integer;
  ss: TStringList;
  i: integer;
  memstr: TMemoryStream;
  strsz: integer;
  v: Variant;
begin
  WriteLn('(s) Client execute');

  X := Link.ReadInteger;
  WriteLn('(s) Recieved int: ' + IntToStr(X));

  ss := TStringList.Create;
  Link.ReadStrings(ss);
  WriteLn('(s) Recieved TStringList length: ' + IntToStr(ss.Count));
  for i := 0 to ss.Count -1 do
    WriteLn('-> ' + ss[i]);
  ss.Free;

  memstr := TMemoryStream.Create;
  strsz := Link.ReadInteger;
  Link.ReadStream(memstr, strsz);
  memstr.Position := 0;
  WriteLn('(s) Recieved stream of size: ' + IntToStr(memstr.Size));
  memstr.Read(v, memstr.Size);
  WriteLn('(s) Recieved variant: ' + VarToStr(v));
  FreeAndNil(memstr);

  Y := -7;
  WriteLn('(s) Transmit int: ' + IntToStr(Y));
  Link.WriteInteger(Y);
end;


procedure StartServer;
var
  Bindings: TIdSocketHandles;
begin
  if Handler = Nil then
    Handler := THandler.Create;

  if TCPServer = Nil then
    begin
      TCPServer := TIdTCPServer.Create(Nil);
      TCPServer.OnConnect := Handler.HandleClientConnect;
      TCPServer.OnDisconnect := Handler.HandleClientDisconnect;
      TCPServer.OnExecute := Handler.HandleClientExecute;
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
