unit Gui;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls,
  Core,
  SocketTypes, SocketMarshall, SocketClient;

type
  TFormMain = class(TForm)
    BtnCheckPrice: TButton;
    MemoLog: TMemo;
    BtnExit: TButton;
    procedure BtnExitClick(Sender: TObject);
    procedure BtnCheckPriceClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  FormMain: TFormMain;

implementation

{$R *.dfm}

procedure TFormMain.BtnCheckPriceClick(Sender: TObject);
var
  price, taxrate, salesprice: integer;
  productname: string;
  product1, product2: Core.TProduct;
  products: Core.TProducts;
  i: integer;
  company1, company2, company3: Core.TCompany;
  companyname: string;
  memstr: TMemoryStream;
  arraylen: integer;
begin
//  price := Core.GetPrice;
{  SocketClient.Transmit('Core.GetPrice'); }
  memstr := SocketClient.OpenWrite('Core.GetPrice');
  SocketClient.CloseWrite('Core.GetPrice', memstr);
{  SocketClient.Receive([@price], [transFlat]); }
  memstr := SocketClient.OpenRead;
  SocketMarshall.Read(memstr, [@price], [transFlat]);
  SocketClient.CloseRead(memstr);

//  taxrate := Core.GetTaxRate;
  SocketClient.Transmit('Core.GetTaxRate');
  SocketClient.Receive([@taxrate], [transFlat]);

//  salesprice := Core.ComputePrice(price, taxrate);
{  SocketClient.Transmit('Core.ComputePrice',
      [@price, @taxrate],
      [SizeOf(price), SizeOf(taxrate)],
      [transFlat, transFlat]); }
  memstr := SocketClient.OpenWrite('Core.ComputePrice');
  SocketMarshall.Write(memstr,
      [@price, @taxrate],
      [SizeOf(price), SizeOf(taxrate)],
      [transFlat, transFlat]);
  SocketClient.CloseWrite('Core.ComputePrice', memstr);
  SocketClient.Receive([@salesprice], [transFlat]);

  MemoLog.Lines.Append(IntToStr(price) + ' + ' + IntToStr(taxrate) + '% = ' +
      IntToStr(salesprice));


  productname := 'Magnet, white';
//  product1 := Core.MakeProduct(productname, salesprice);
  SocketClient.Transmit('Core.MakeProduct',
      [@productname, @salesprice],
      [Length(productname), SizeOf(salesprice)],
      [transString, transFlat]);
  SocketClient.Receive([@product1], [transFlat]);

  MemoLog.Lines.Append(' * ' + product1.Name + ': ' + IntToStr(product1.Price));

//  products := Core.MakeProducts;
  SocketClient.Transmit('Core.MakeProducts');
  memstr := SocketClient.OpenRead;
  SocketMarshall.Read(memstr, [@arraylen], [transFlat]);
  SetLength(products, arraylen);
  for i := Low(products) to High(products) do
    SocketMarshall.Read(memstr, [@products[i]], [transFlat]);
  SocketClient.CloseRead(memstr);
  for i := Low(products) to High(products) do
    MemoLog.Lines.Append(' ' + IntToStr(i) + '. ' + products[i].Name + ': ' + IntToStr(products[i].Price));


  company1 := Core.TCompany.Create('Acme', product1);

//  Core.Tradeshow.Register(company1);
  SocketClient.Transmit('Core.Tradeshow.Register',
      [@company1.Name, @company1.Product],
      [Length(company1.Name), SizeOf(company1.Product)],
      [transString, transFlat]);

  product2 := Core.MakeProduct('Screwdriver', 290);
  company2 := Core.TCompany.Create('Abysmal', product2);

//  Core.Tradeshow.Register(company2);
  SocketClient.Transmit('Core.Tradeshow.Register',
      [@company2.Name, @company2.Product],
      [Length(company2.Name), SizeOf(company2.Product)],
      [transString, transFlat]);

  companyname := 'Acme';
//  company3 := Core.Tradeshow.Find(companyname);
  SocketClient.Transmit('Core.Tradeshow.Find',
      [@companyname],
      [Length(companyname)],
      [transString]);
  company3 := Core.TCompany.Create;
  SocketClient.Receive(
      [@company3.Name, @company3.Product],
      [transString, transFlat]);

  MemoLog.Lines.Append(company3.Print);

end;

procedure TFormMain.BtnExitClick(Sender: TObject);
begin
  Self.Close;
end;

end.
