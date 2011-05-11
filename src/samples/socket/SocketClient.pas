unit SocketClient;

interface

procedure Connect;
procedure Disconnect;


implementation

uses
  SysUtils, Classes, Variants,
  IdTCPClient, IdTCPConnection,
  SocketInfo;

type
  THandler = class(TObject)
    public
      procedure HandleConnected(Sender: TObject);
      procedure HandleDisconnected(Sender: TObject);
  end;

var
  TCPClient: TIdTCPClient;
  Handler: THandler;
  Link: TIdTCPConnection;


procedure THandler.HandleConnected(Sender: TObject);
var
  X: integer;
  ss: TStringList;
  memstr: TMemoryStream;
  v, v2: Variant;
begin
  System.WriteLn('(c) Client connected');
  Link := TCPClient;

  X := -3;
  WriteLn('(c) Transmit int: ' + IntToStr(X));
  Link.WriteInteger(X);

  ss := TStringList.Create;
  ss.Add('fst');
  ss.Add('snd');
  WriteLn('(c) Transmit TStringList length: ' + IntToStr(ss.Count));
  Link.WriteStrings(ss, true);
  ss.Free;

  v := true;
  memstr := TMemoryStream.Create;
//  wr := TWriter.Create(memstr, $ff);
  memstr.Write(v, SizeOf(v));
//  rr := TReader.Create(memstr, $ff);
//  b := rr.ReadBoolean;
  memstr.Position := 0;
  memstr.Read(v2, memstr.Size);
  WriteLn('(c) Transmit stream w/ variant: ' + VarToStr(v2));
  WriteLn('(c) Transmit stream size: ' + IntToStr(memstr.Size));
  Link.WriteInteger(memstr.Size);
  WriteLn('(c) Transmit stream');
  Link.OpenWriteBuffer;
  Link.WriteStream(memstr);
  Link.CloseWriteBuffer;
  FreeAndNil(memstr);

  WriteLn('(c) Received int: ' + IntToStr(Link.ReadInteger));
end;

procedure THandler.HandleDisconnected(Sender: TObject);
begin
  System.WriteLn('(c) Client disconnected');
  Link := Nil;
end;


procedure Connect;
begin
  if Handler = Nil then
    Handler := THandler.Create;

  if TCPClient = Nil then
    begin
      TCPClient := TIdTCPClient.Create(Nil);
      TCPClient.OnConnected := Handler.HandleConnected;
      TCPClient.OnDisconnected := Handler.HandleDisconnected;
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
