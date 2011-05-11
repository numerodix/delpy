unit Core;

interface

function GetPrice: integer;
function GetTaxRate: integer;
function ComputePrice(price: integer; taxrate: integer): integer;


type
  TProduct = record
    Name: string[40];
    Price: integer;
  end;
  TProducts = array of TProduct;

function MakeProduct(name: string; price: integer): TProduct;
function MakeProducts: TProducts;


type
  TCompany = class
      Name: string;
      Product: TProduct;
    public
      constructor Create; overload;
      constructor Create(Name: string; Product: TProduct); overload;
      function Print: string;
  end;

type
  TTradeShow = class
      Companies: array of TCompany;
    public
      procedure Register(company: TCompany);
      function Find(name: string): TCompany;
  end;

var
  Tradeshow: TTradeShow;


implementation

uses
  Classes, SysUtils, Windows;


function GetRandom(lowerbound, upperbound: integer; seed: integer = -1): integer;
var
  hours, mins, secs, millisecs: Word;
begin
  SysUtils.DecodeTime(Now, hours, mins, secs, millisecs);
  System.RandSeed := millisecs;
  if seed <> -1 then
    System.RandSeed := millisecs - seed;
  Result := lowerbound + System.Random(upperbound - lowerbound);
end;

function GetPrice: integer;
begin
  Result := 100;
end;

function GetTaxRate: integer;
begin
  Result := GetRandom(1, 50);
end;

function ComputePrice(price: integer; taxrate: integer): integer;
begin
  Result := Round(price * (1 + (taxrate / 100)));
end;


function MakeProduct(name: string; price: integer): TProduct;
var
  product: TProduct;
begin
  product.Name := name;
  product.Price := price;
  Result := product;
end;

function MakeProducts: TProducts;
var
  len, i: integer;
  seed, num: integer;
begin
  len := GetRandom(5, 10);
  SetLength(Result, len);
  seed := 7;
  for i := Low(Result) to High(Result) do
    begin
      num := GetRandom(1, 100, seed);
      seed := num;
      Result[i] := MakeProduct('Product ' + IntToStr(i), num);
    end;
end;


constructor TCompany.Create;
begin
  inherited;
end;

constructor TCompany.Create(Name: string; Product: TProduct);
begin
  self.Name := Name;
  self.Product := Product;
end;

function TCompany.Print: string;
begin
  Result := ' :: company:' + self.Name + ', assets:' +
      IntToStr(self.Product.Price);
end;


procedure TTradeShow.Register(company: TCompany);
begin
  SetLength(self.Companies, 1 + Length(self.Companies));
  self.Companies[Length(self.Companies) - 1] := company;
end;

function TTradeShow.Find(name: string): TCompany;
var
  i: integer;
begin
  Result := nil;
  for i := 0 to High(self.Companies) do
    if self.Companies[i].Name = name then
      Result := self.Companies[i];
  if not Assigned(Result) then
    WriteLn('Error: Company lookup failed: ' + name);
end;


initialization
  Tradeshow := TTradeShow.Create;

end.
