program RunServer;

uses
  SysUtils, Classes,
  SocketServer;

begin
  try
    SocketServer.StartServer;
  except on E:Exception do
    System.WriteLn(E.Message);
  end;
end.
