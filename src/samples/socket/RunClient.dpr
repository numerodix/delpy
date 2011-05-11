program RunClient;

uses
  SysUtils, Classes,
  SocketClient;

begin
  try
    SocketClient.Connect;
  except on E:Exception do
    System.WriteLn(E.Message);
  end;
end.
