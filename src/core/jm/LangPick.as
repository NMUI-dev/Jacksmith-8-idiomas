package jm
{
   import flash.display.Sprite;
   import flash.events.Event;
   import flash.events.MouseEvent;
   import flash.text.Font;
   import flash.text.TextField;
   import flash.text.TextFormat;

   /** Primer arranque: elegir idioma antes que nada. Se dibuja con los colores y la letra del juego. */
   public class LangPick
   {
      private static var root:Sprite;
      private static const FONT:String = "Alegreya Sans SC ExtraBold";

      public static function show():void
      {
         var holder:Object = JM.game.resizerClip;
         root = new Sprite();
         root.graphics.beginFill(0x0B0B0B, 0.93);
         root.graphics.drawRect(-900, -400, 2440, 1280);
         root.graphics.endFill();
         var n:int = JM.langs.length;
         // (19-10-2026, 10 idiomas) con más de 5, dos columnas: en una sola no cabían en la pantalla de 480 de alto
         var cols:int = n > 5 ? 2 : 1;
         var rows:int = Math.ceil(n / cols);
         var pw:Number = cols == 2 ? 470 : 300;
         var ph:Number = 132 + rows * 44;
         var py:Number = 240 - ph / 2;
         // panel con el mismo aspecto que el de ajustes
         root.graphics.beginFill(0x101010); root.graphics.drawRoundRect(320 - pw / 2 - 6, py - 6, pw + 12, ph + 12, 22, 22); root.graphics.endFill();
         root.graphics.beginFill(0x2E2E2E); root.graphics.drawRoundRect(320 - pw / 2, py, pw, ph, 16, 16); root.graphics.endFill();
         root.graphics.beginFill(0x1B1B1B); root.graphics.drawRoundRect(320 - pw / 2, py, pw, 40, 16, 16); root.graphics.endFill();
         root.graphics.beginFill(0x2E2E2E); root.graphics.drawRect(320 - pw / 2, py + 32, pw, 10); root.graphics.endFill();
         label("Idioma / Language", 320, py + 4, 22, 0xCCCCCC, pw - 10);
         label("Elige tu idioma / Choose your language", 320, py + 44, 12, 0xBFBEBE, pw - 10);
         var codes:Array = JM.langs.concat();
         codes.sort(function(a:String, b:String):int { return a == "es" ? -1 : (b == "es" ? 1 : (a == "en" ? -1 : (b == "en" ? 1 : (a < b ? -1 : 1)))); });
         for(var i:int = 0; i < codes.length; i++)
            button(codes[i], cols == 2 ? 320 + (i % 2 == 0 ? -113 : 113) : 320, py + 70 + Math.floor(i / cols) * 44);
         label(String(JM.t("More languages coming soon")), 320, py + ph - 40, 11, 0xBFBEBE, pw - 10, null, 2);
         holder.addChild(root);
         root.addEventListener(Event.ENTER_FRAME, keepTop);
      }

      private static function hasFont():Boolean
      {
         for each(var f:Font in Font.enumerateFonts(false)) if(f.fontName == FONT) return true;
         return false;
      }

      private static function label(s:String, cx:Number, y:Number, size:Number, color:uint, w:Number, parent:Sprite = null, lines:int = 1):TextField
      {
         var tf:TextField = new TextField();
         var emb:Boolean = hasFont();
         tf.embedFonts = emb; tf.selectable = false; tf.mouseEnabled = false;
         tf.antiAliasType = "advanced";
         tf.defaultTextFormat = new TextFormat(emb ? FONT : "Arial", size, color, null, null, null, null, null, "center");
         tf.width = w; tf.height = (size * 1.6 + 4) * lines; tf.multiline = lines > 1;
         tf.x = cx - w / 2; tf.y = y;
         tf.text = s;
         // (nombres largos: «Chinesisch (vereinfacht)») se reduce la letra lo justo para que quepa
         var fmt:TextFormat = tf.getTextFormat();
         while(tf.textWidth > w - 8 && Number(fmt.size) > 9) { fmt.size = Number(fmt.size) - 1; tf.setTextFormat(fmt); }
         (parent == null ? root : parent).addChild(tf);
         return tf;
      }

      private static function button(code:String, cx:Number, y:Number):void
      {
         var b:Sprite = new Sprite();
         b.x = cx; b.y = y;
         paint(b, false);
         // (primer arranque: aún no hay idioma elegido; cada idioma escrito en SU idioma —日本語, Русский— para encontrarlo)
         label(JM.ownName(code), 0, 3, 20, 0x71361A, 190, b);
         b.buttonMode = true; b.mouseChildren = false;
         b.name = "lang_" + code;
         b.addEventListener(MouseEvent.ROLL_OVER, function(e:MouseEvent):void { paint(b, true); });
         b.addEventListener(MouseEvent.ROLL_OUT, function(e:MouseEvent):void { paint(b, false); });
         b.addEventListener(MouseEvent.MOUSE_DOWN, function(e:MouseEvent):void { choose(code); });
         root.addChild(b);
      }

      private static function paint(b:Sprite, over:Boolean):void
      {
         b.graphics.clear();
         b.graphics.beginFill(0x080300); b.graphics.drawRoundRect(-104, -4, 208, 42, 16, 16); b.graphics.endFill();
         b.graphics.beginFill(0xAF5700); b.graphics.drawRoundRect(-101, -1, 202, 36, 12, 12); b.graphics.endFill();
         b.graphics.beginFill(over ? 0xFFD86F : 0xFFC835); b.graphics.drawRoundRect(-98, 2, 196, 30, 9, 9); b.graphics.endFill();
         if(!over) { b.graphics.beginFill(0xFFD86F); b.graphics.drawRoundRect(-98, 2, 196, 12, 9, 9); b.graphics.endFill(); }
      }

      private static function keepTop(e:Event):void
      {
         try { if(root.parent != null && root.parent.getChildIndex(root) != root.parent.numChildren - 1) root.parent.setChildIndex(root, root.parent.numChildren - 1); }
         catch(err:Error) {}
      }

      private static function choose(code:String):void
      {
         try { JM.game.soundManager.playSound("buttonclick.wav"); } catch(e:Error) {}
         root.removeEventListener(Event.ENTER_FRAME, keepTop);
         if(root.parent != null) root.parent.removeChild(root);
         root = null;
         JM.firstRun = false;
         if(code != JM.lang) JM.setLang(code);
         JM.saveSettings();
      }
   }
}
