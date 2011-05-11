# Prettify source code

Source code that is badly formatted is hard to understand:

	procedure StartServer; var Bindings: TIdSocketHandles;
	begin if Handler = Nil then
	Handler := THandler.Create;
	if TCPServer = Nil then
	begin
	TCPServer := TIdTCPServer.Create(Nil);
	TCPServer.OnConnect := Handler.HandleClientConnect;
	TCPServer.OnDisconnect := Handler.HandleClientDisconnect;
	TCPServer.OnExecute := Handler.HandleClientExecute;
	end; if not TCPServer.Active then
	begin
	Bindings := TIdSocketHandles.Create(TCPServer);
	try with Bindings.Add do
	begin
	IP := SocketConnectionIp;
	Port := SocketConnectionPort;
	end;
	try
	TCPServer.Bindings := Bindings; TCPServer.Active := True;
	except on E:Exception do System.WriteLn(E.Message);
	end;
	finally
	Bindings.Free; end;

	if TCPServer.Active then
	System.WriteLn('(s) SocketServer running on '
	+ TCPServer.Bindings[0].IP + ':' + IntToStr(TCPServer.Bindings[0].Port));
	end;
	end;

The tool `delphiparser.py` can reformat the code. You can run it on a single
file or on the entire codebase.

	$ delphiparser.py SocketServer.pas -u

The resulting formatting:

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
			except
			on E: Exception do
			  System.WriteLn(E.Message);
			end;
		  finally
			Bindings.Free;
		  end;
		  if TCPServer.Active then
			System.WriteLn('(s) SocketServer running on ' + TCPServer.Bindings[0].IP + ':' + IntToStr(TCPServer.Bindings[0].Port));
		end;
	end;

