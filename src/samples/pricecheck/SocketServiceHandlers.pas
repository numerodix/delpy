unit SocketServiceHandlers;

interface

uses
  SysUtils, Classes, Variants,
  IdTCPConnection,
  SocketServer, SocketTypes, SocketMarshall,
  Core;


procedure InitIndex;

procedure Serve__Core_GetPrice(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);

procedure Serve__Core_GetTaxRate(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);

procedure Serve__Core_ComputePrice(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);

procedure Serve__Core_MakeProduct(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);

procedure Serve__Core_MakeProducts(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);

procedure Serve__Core_Tradeshow_Register(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);

procedure Serve__Core_Tradeshow_Find(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);

var
  HandlerIndex: TServiceHandlerIndex;


implementation

procedure InitIndex;
begin
  if HandlerIndex = nil then
    begin
      HandlerIndex := TServiceHandlerIndex.Create;
      HandlerIndex.Register('Core.GetPrice', Serve__Core_GetPrice);
      HandlerIndex.Register('Core.GetTaxRate', Serve__Core_GetTaxRate);
      HandlerIndex.Register('Core.ComputePrice', Serve__Core_ComputePrice);
      HandlerIndex.Register('Core.MakeProduct', Serve__Core_MakeProduct);
      HandlerIndex.Register('Core.MakeProducts', Serve__Core_MakeProducts);
      HandlerIndex.Register('Core.Tradeshow.Register', Serve__Core_Tradeshow_Register);
      HandlerIndex.Register('Core.Tradeshow.Find', Serve__Core_Tradeshow_Find);
    end;
end;

procedure Serve__Core_GetPrice(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);
var
  price: integer;
begin
  price := Core.GetPrice;
  SocketMarshall.Write(outstream,
      [@price], [SizeOf(price)], [transFlat]);
end;

procedure Serve__Core_GetTaxRate(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);
var
  taxrate: integer;
begin
  taxrate := Core.GetTaxRate;
  SocketMarshall.Write(outstream,
      [@taxrate], [SizeOf(taxrate)], [transFlat]);
end;

procedure Serve__Core_ComputePrice(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);
var
  price, taxrate, salesprice: integer;
begin
  SocketMarshall.Read(instream,
      [@price, @taxrate],
      [transFlat, transFlat]);
  salesprice := Core.ComputePrice(price, taxrate);
  SocketMarshall.Write(outstream,
      [@salesprice], [SizeOf(salesprice)], [transFlat]);
end;

procedure Serve__Core_MakeProduct(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);
var
  productname: string;
  salesprice: integer;
  product: Core.TProduct;
begin
  SocketMarshall.Read(instream,
      [@productname, @salesprice],
      [transString, transFlat]);
  product := Core.MakeProduct(productname, salesprice);
  SocketMarshall.Write(outstream, [@product], [SizeOf(product)], [transFlat]);
end;

procedure Serve__Core_MakeProducts(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);
var
  products: Core.TProducts;
  len, i: integer;
begin
  products := Core.MakeProducts;
  len := Length(products);
  SocketMarshall.Write(outstream, [@len], [SizeOf(len)], [transFlat]);
  for i := Low(products) to High(products) do
    SocketMarshall.Write(outstream, [@products[i]], [SizeOf(products[i])], [transFlat]);
end;

procedure Serve__Core_Tradeshow_Register(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);
var
  obj1: Core.TCompany;
begin
  obj1 := Core.TCompany.Create;
  SocketMarshall.Read(instream,
    [@obj1.Name, @obj1.Product],
    [transString, transFlat]);
  Core.Tradeshow.Register(obj1);
end;

procedure Serve__Core_Tradeshow_Find(
    const instream: TMemoryStream;
    const outstream: TMemoryStream);
var
  s1: string;
  obj1: Core.TCompany;
begin
  SocketMarshall.Read(instream, [@s1], [transString]);
  obj1 := Core.Tradeshow.Find(s1);
  SocketMarshall.Write(outstream,
    [@obj1.Name, @obj1.Product],
    [Length(obj1.Name), SizeOf(obj1.Product)],
    [transString, transFlat]);
end;

end.
