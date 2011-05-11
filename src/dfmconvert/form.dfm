object MainGui: TMainGui
  Left = 0
  Top = 0
  Caption = 'Abysmal'
  ClientHeight = 216
  ClientWidth = 426
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object BtnLoad: TButton
    Left = 0
    Top = 191
    Width = 75
    Height = 25
    Caption = 'Load'
    TabOrder = 0
    OnClick = BtnLoadClick
  end
  object Multiline: TMemo
    Left = 0
    Top = 0
    Width = 425
    Height = 193
    TabOrder = 1
  end
  object BtnQuit: TButton
    Left = 350
    Top = 191
    Width = 75
    Height = 25
    Caption = 'Quit'
    TabOrder = 2
    OnClick = BtnQuitClick
  end
end
