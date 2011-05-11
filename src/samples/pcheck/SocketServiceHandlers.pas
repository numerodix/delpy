unit SocketServiceHandlers;

interface

uses
  SysUtils, Classes, IdTCPConnection, SocketServer, SocketMarshall, SocketTypes,
  Core;

var
  HandlerIndex: TServiceHandlerIndex;

procedure InitIndex;

procedure Serve__Core_GetPrice(
  const instream: TMemoryStream; 
  const outstream: TMemoryStream
);

procedure Serve__Core_GetTaxRate(
  const instream: TMemoryStream; 
  const outstream: TMemoryStream
);

procedure Serve__Core_ComputePrice(
  const instream: TMemoryStream; 
  const outstream: TMemoryStream
);

implementation

procedure InitIndex;
begin
  if HandlerIndex = nil then
    begin
      HandlerIndex := TServiceHandlerIndex.Create;
      HandlerIndex.Register('Core.GetPrice', Serve__Core_GetPrice);
      HandlerIndex.Register(
        'Core.GetTaxRate', 
        Serve__Core_GetTaxRate
      );
      HandlerIndex.Register(
        'Core.ComputePrice', 
        Serve__Core_ComputePrice
      );
    end;
end;

procedure Serve__Core_GetPrice(
  const instream: TMemoryStream; 
  const outstream: TMemoryStream
);
var
  price: integer;
begin
  price := Core.GetPrice;
  SocketMarshall.Write(
    outstream, 
    [@price], 
    [SizeOf(price)], 
    [SocketTypes.transFlat]
  );
end;

procedure Serve__Core_GetTaxRate(
  const instream: TMemoryStream; 
  const outstream: TMemoryStream
);
var
  taxrate: integer;
begin
  taxrate := Core.GetTaxRate;
  SocketMarshall.Write(
    outstream, 
    [@taxrate], 
    [SizeOf(taxrate)], 
    [SocketTypes.transFlat]
  );
end;

procedure Serve__Core_ComputePrice(
  const instream: TMemoryStream; 
  const outstream: TMemoryStream
);
var
  price, taxrate, salesprice: integer;
begin
  SocketMarshall.Read(
    instream, 
    [@price, @taxrate], 
    [SocketTypes.transFlat, SocketTypes.transFlat]
  );
  salesprice := Core.ComputePrice(price, taxrate);
  SocketMarshall.Write(
    outstream, 
    [@salesprice], 
    [SizeOf(salesprice)], 
    [SocketTypes.transFlat]
  );
end;

end.
