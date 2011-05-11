unit SocketTypes;

interface

uses
  SysUtils, Classes,
  IdTCPConnection;


type
  THost = (
      hostClient, hostServer
    );

  TCallEvent = (
      eventCall, eventReturn
    );

  TTransmissionType = (
      transString, transFlat
    );

  TCallId = class
      Funcname: string;
      Id: integer;
    public
      constructor Create; overload;
      constructor Create(funcname: string; id: integer); overload;
  end;

  TServiceHandler = procedure (
      const instream: TMemoryStream;
      const outstream: TMemoryStream);


  TServiceHandlerPair = class
      FuncName: string;
      Func: TServiceHandler;
    public
      constructor Create(funcname: string; func: TServiceHandler);
  end;

  TServiceHandlerIndex = class
      Index: array of TServiceHandlerPair;
    public
      procedure Register(funcname: string; func: TServiceHandler);
      function Find(funcname: string): TServiceHandler;
  end;

procedure FakeLatency(payload: integer);
procedure WriteTransmit(event: TCallEvent; host: THost; callid: TCallId; payload: integer);
procedure WriteReceived(event: TCallEvent; host: THost; callid: TCallId; payload, latency: integer);


implementation

procedure FakeLatency(payload: integer);
var
  delay: integer;
begin
  delay := 75 + payload;
//  WriteLn('Fake latency: ' + IntToStr(delay) + 'ms');
  Sleep(delay);
end;

procedure WriteEvent(transmit: boolean; event: TCallEvent; host: THost; callid: TCallId; payload, latency: integer);
var
  prefix, event_s, latency_s: string;
begin
  prefix := '(c)';
  if host = hostServer then
    prefix := '(s)';

  event_s := 'Transmit';
  if not transmit then
    event_s := 'Received';

  if event = eventCall then
    event_s := event_s + ' call'
  else
    event_s := event_s + ' result';

  latency_s := '  {' + IntToStr(latency) + 'ms}';
  if latency = -1 then
    latency_s := '';

  WriteLn(prefix
      + ' [' + IntToStr(callid.Id) + '] '
      + event_s + ': ' + callid.Funcname
      + ' <' + IntToStr(payload) + 'b>'
      + latency_s);
end;

procedure WriteTransmit(event: TCallEvent; host: THost; callid: TCallId; payload: integer);
begin
  WriteEvent(true, event, host, callid, payload, -1);
end;

procedure WriteReceived(event: TCallEvent; host: THost; callid: TCallId; payload, latency: integer);
begin
  WriteEvent(false, event, host, callid, payload, latency);
end;


constructor TCallId.Create;
begin
  inherited;
end;

constructor TCallId.Create(funcname: string; id: integer);
begin
  self.Funcname := funcname;
  self.Id := id;
end;


constructor TServiceHandlerPair.Create(funcname: string; func: TServiceHandler);
begin
  self.FuncName := funcname;
  self.Func := func;
end;

procedure TServiceHandlerIndex.Register(funcname: string; func: TServiceHandler);
var
  pair: TServiceHandlerPair;
begin
  pair := TServiceHandlerPair.Create(funcname, func);
  SetLength(self.Index, 1 + Length(self.Index));
  self.Index[High(self.Index)] := pair;
end;

function TServiceHandlerIndex.Find(funcname: string): TServiceHandler;
var
  i: integer;
begin
  Result := nil;
  for i := Low(self.Index) to High(self.Index) do
    if self.Index[i].FuncName = funcname then
      Result := self.Index[i].Func;
  if not Assigned(Result) then
    WriteLn('Error: Function lookup failed: ' + funcname);
//    raise Exception.Create('Invalid function call to: ' + funcname);
end;

end.
