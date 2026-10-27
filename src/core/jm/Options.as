package jm
{
   import flash.display.Bitmap;
   import flash.display.BitmapData;
   import flash.display.DisplayObject;
   import flash.display.DisplayObjectContainer;
   import flash.display.MovieClip;
   import flash.display.Shape;
   import flash.display.Sprite;
   import flash.events.Event;
   import flash.events.MouseEvent;
   import flash.geom.Matrix;
   import flash.geom.Rectangle;
   import flash.text.TextField;
   import flash.text.TextFormat;
   import flash.utils.getDefinitionByName;

   /**
    * Pantalla de ajustes del juego, reordenada con sus propias piezas:
    *   1) Idioma (primera opción) + nota «Próximamente más idiomas»
    *   2) Pantalla completa, tamaño de ventana, calidad gráfica
    *   3) Sonido, todo junto: silenciar efectos / música, volumen general y un deslizador por grupo de sonidos
    *   4) Créditos del juego y botón de salir
    * Todo cuelga de `clip.inside`, así que escala con el juego en cualquier resolución.
    */
   public class Options
   {
      private static const SNAP:Number = 6;            // resolución de las copias de piezas del juego
      private static const CX:Number = 241.5;          // centro del panel (coordenadas de `inside`)
      private static const LX:Number = 92;             // columna de etiquetas
      private static const LW:Number = 118;
      private static const CTRL:Number = 214;          // columna de controles

      private static var screen:Object;
      private static var inside:MovieClip;
      private static var langHead:Sprite;
      private static var langLabel:TextField;
      private static var noteTf:TextField;
      private static var pop:MovieClip;
      private static var popParts:Array = [];
      private static var sliders:Array = [];
      private static var drag:Object = null;
      private static var extraLabels:Array = [];
      private static var own:Array = [];
      private static var modParts:Array = [];          // todo lo que añade el mod a `inside` (se oculta con la confirmación de salir)
      private static var quitShown:Boolean = false;

      public static function build(scr:Object):void
      {
         try { layout(scr); }
         catch(e:Error) { JM.log("opciones: " + e.message + " " + e.getStackTrace()); }
         JM.emit("options", scr);
      }

      private static function byY(y:Number, tol:Number = 4):TextField
      {
         for(var i:int = 0; i < inside.numChildren; i++)
         {
            var d:DisplayObject = inside.getChildAt(i);
            if(d is TextField && d.name.indexOf("instance") == 0 && Math.abs(d.y - y) < tol) return d as TextField;
         }
         return null;
      }

      private static function layout(scr:Object):void
      {
         screen = scr;
         inside = scr.clip.inside;
         sliders = []; extraLabels = []; pop = null; popParts = []; modParts = []; quitShown = false;
         var lDev:TextField = byY(35.5), lFull:TextField = byY(101.2), lWin:TextField = byY(144.2), lQual:TextField = byY(188.5), lVol:TextField = byY(239.9);
         var vp:MovieClip = inside.volumepanel;
         if(lDev == null || lFull == null || lWin == null || lQual == null || lVol == null || vp == null) { JM.log("opciones: la pantalla no es la esperada; se deja como está"); return; }

         hideLines();

         // ---- 1) idioma
         var row:Number = 40;
         var lLang:TextField = cloneLabel(lFull, "Language:");
         putLabel(lLang, row);
         JM.setText([lLang, "Language:"]);
         langHead = makeLangHead(inside.window_dropdown);
         langHead.x = CTRL; langHead.y = row;
         inside.addChild(langHead);
         noteTf = cloneLabel(inside.version_txt, "More languages coming soon");
         var nf:TextFormat = noteTf.defaultTextFormat; nf.size = 11; nf.color = 0xBFBEBE; nf.align = "center"; noteTf.defaultTextFormat = nf;
         // (19-10-2026) en los idiomas nuevos la nota lleva una 2.ª línea: aviso de traducción con IA
         noteTf.width = 167.3 / noteTf.scaleX; noteTf.height = 26 / noteTf.scaleY; noteTf.multiline = true; noteTf.wordWrap = false;
         noteTf.x = CTRL; noteTf.y = row + 17;
         JM.setText([noteTf, "More languages coming soon"]);

         // ---- 2) pantalla
         row = 78;  putLabel(lFull, row); inside.fullscreen_btn.x = CTRL; inside.fullscreen_btn.y = row + 1.5;
         row = 102; putLabel(lWin, row);  inside.window_dropdown.x = CTRL; inside.window_dropdown.y = row;
         row = 126; putLabel(lQual, row); inside.quality_dropdown.x = CTRL; inside.quality_dropdown.y = row;
         separator(150);

         // ---- 3) sonido
         row = 156;
         placeMute(inside.soundfx, 150, row);
         placeMute(inside.music, 330, row);
         // volumen general (deslizador original) + un deslizador por grupo
         var cols:Array = [LX, 245];
         var LABW:Number = 54; var TRK:Number = 56; var RIGHT:Number = 397;
         own = [];
         var all:Array = [{id:"*", en:"Master:"}];
         for each(var g:Object in JM.groups) all.push({id:g.id, en:g.en + ":"});
         var track:BitmapData = snapshot(vp.getChildAt(0));
         var tb:Rectangle = vp.getChildAt(0).getBounds(vp);
         for(var i:int = 0; i < all.length; i++)
         {
            var col:Number = cols[i % 2];
            var ry:Number = 183 + Math.floor(i / 2) * 20;
            var lab:TextField = (i == 0) ? lVol : cloneLabel(lVol, all[i].en);
            var lf:TextFormat = lab.defaultTextFormat; lf.color = 0xFFFFFF; lf.align = "center"; lab.defaultTextFormat = lf;
            lab.width = LABW / lab.scaleX; lab.x = col; lab.y = ry - 11;
            JM.setText([lab, all[i].en]);
            JM.refit(lab);
            own.push({tf:lab, en:all[i].en});
            var sp:Sprite;
            if(i == 0) { vp.scaleX = vp.scaleY = 0.8; vp.y = ry; snapLeft(vp, vp.getChildAt(0), col + TRK, RIGHT); }
            else
            {
               sp = new Sprite();
               var bm:Bitmap = new Bitmap(track, "auto", true);
               bm.scaleX = bm.scaleY = 1 / SNAP; bm.x = tb.x; bm.y = tb.y;
               sp.addChild(bm);
               var knob:MovieClip = new (Object(vp.slider).constructor as Class)();
               knob.gotoAndStop(1); knob.y = vp.slider.y; knob.buttonMode = true;
               knob.x = scr.volumeSliderStartX + JM.getVol(all[i].id) * scr.volumeSliderRange;
               sp.addChild(knob);
               sp.scaleX = sp.scaleY = 0.8; sp.y = ry;
               inside.addChild(sp);
               modParts.push(sp);
               snapLeft(sp, bm, col + TRK, RIGHT);
               var s:Object = {id:all[i].id, knob:knob};
               sliders.push(s);
               knob.addEventListener(MouseEvent.MOUSE_DOWN, onKnobDown);
               knob.addEventListener(MouseEvent.ROLL_OVER, onKnobOver);
               knob.addEventListener(MouseEvent.ROLL_OUT, onKnobOut);
            }
         }
         separator(246);

         // ---- 4) créditos y salir
         var cxL:Number = 160;
         lDev.x = cxL - lDev.width / 2; lDev.y = 249;
         inside.logo.scaleX *= 0.88; inside.logo.scaleY *= 0.88;
         inside.logo.x = cxL - inside.logo.width / 2; inside.logo.y = 263;
         inside.version_txt.x = cxL - inside.version_txt.width / 2; inside.version_txt.y = 289.5;
         inside.quit_btn.x = 322 - inside.quit_btn.width / 2; inside.quit_btn.y = 264;
         // rayita suelta del diseño original (quedaba tapada por el logo)
         for(var k:int = 0; k < inside.numChildren; k++)
         {
            var dd:DisplayObject = inside.getChildAt(k);
            if(dd is Shape && dd.width < 4 && dd.height < 30) dd.visible = false;
         }

         modParts.push(langHead);
         modParts.push(inside.version_txt);               // el mod lo bajó a y=289.5 y asomaba bajo la confirmación
         for each(var xl:TextField in extraLabels) modParts.push(xl);
         scr.clip.addEventListener(Event.REMOVED_FROM_STAGE, onGone);
         scr.clip.addEventListener(Event.ENTER_FRAME, watchQuit);
      }

      /**
       * «¿Seguro que quieres salir del juego?» (`inside.confirmquit`, lo abre el juego con Escape o con Salir) va DENTRO
       * de la misma ventana; lo que añade el mod se colocó después y quedaba dibujado encima de No / Sí.
       * Mientras se vea la confirmación: piezas del mod ocultas (sin clics) y la confirmación arriba del todo.
       */
      private static function watchQuit(e:Event):void
      {
         try
         {
            if(inside == null) return;
            var cq:DisplayObject = inside.confirmquit as DisplayObject;
            if(cq == null) return;
            var on:Boolean = cq.visible;
            if(on == quitShown) return;
            quitShown = on;
            if(on)
            {
               if(drag != null) onKnobUp();
               closeLang();
               if(cq.parent == inside) inside.setChildIndex(cq, inside.numChildren - 1);
            }
            for each(var d:DisplayObject in modParts) if(d != null) d.visible = !on;
         }
         catch(err:Error) {}
      }

      // ------------------------------------------------------------------ piezas
      /** Copia en mapa de bits (a alta resolución) de una pieza vectorial del juego. */
      private static function snapshot(d:DisplayObject):BitmapData
      {
         var b:Rectangle = d.getBounds(d);
         var bd:BitmapData = new BitmapData(Math.ceil(b.width * SNAP) + 2, Math.ceil(b.height * SNAP) + 2, true, 0);
         bd.draw(d, new Matrix(SNAP, 0, 0, SNAP, -b.x * SNAP, -b.y * SNAP), null, null, null, true);
         return bd;
      }

      private static function cloneLabel(ref:TextField, text:String):TextField
      {
         var tf:TextField = new TextField();
         tf.embedFonts = true; tf.selectable = false; tf.mouseEnabled = false; tf.multiline = false; tf.wordWrap = false;
         tf.antiAliasType = ref.antiAliasType; tf.gridFitType = ref.gridFitType; tf.sharpness = ref.sharpness; tf.thickness = ref.thickness;
         tf.defaultTextFormat = ref.defaultTextFormat;
         tf.scaleX = ref.scaleX; tf.scaleY = ref.scaleY;
         tf.width = ref.width / ref.scaleX; tf.height = ref.height / ref.scaleY;
         tf.filters = ref.filters;
         inside.addChild(tf);
         extraLabels.push(tf);
         return tf;
      }

      private static function putLabel(tf:TextField, row:Number):void
      {
         tf.width = LW / tf.scaleX;
         tf.x = LX; tf.y = row - 3.5;
         if(tf.text.length > 0) JM.refit(tf);
      }

      /** Coloca `cont` de modo que el borde izquierdo REAL de `track` quede en x (y nunca pase de `right`). */
      private static function snapLeft(cont:DisplayObject, track:DisplayObject, x:Number, right:Number):void
      {
         var b:Rectangle = track.getBounds(inside);
         cont.x += x - b.x;
         b = track.getBounds(inside);
         var over:Number = (b.right + 7) - right;          // 7 = medio botón deslizante al tope
         if(over > 0) cont.x -= over;
      }

      private static function placeMute(c:MovieClip, btnCenterX:Number, row:Number):void
      {
         // la etiqueta no puede pisar el botón: se separa según lo que mide el texto ya traducido
         try
         {
            var lab:TextField = null; var btn:DisplayObject = null;
            for(var i:int = 0; i < c.numChildren; i++)
            {
               var d:DisplayObject = c.getChildAt(i);
               if(d is TextField) lab = d as TextField;
               else if(btn == null || d.width > btn.width) btn = d;
            }
            if(lab != null && btn != null)
            {
               var bb:Rectangle = btn.getBounds(c);
               var tw:Number = lab.textWidth + 6;
               var mid:Number = lab.x + lab.width / 2;
               if(mid < bb.x + bb.width / 2) lab.x = bb.x - 5 - (lab.width + tw) / 2;      // etiqueta a la izquierda
               else lab.x = bb.right + 5 - (lab.width - tw) / 2;                             // etiqueta a la derecha
            }
         }
         catch(e:Error) {}
         // el clip trae su etiqueta y su botón: se centra el conjunto en btnCenterX
         var b:Rectangle = c.getBounds(inside);
         c.x += btnCenterX - (b.x + b.width / 2);
         c.y += (row + 10) - (b.y + b.height / 2);
      }

      /** Tapa los separadores dibujados en el fondo (ya no coinciden con las filas). */
      private static var lineColor:uint = 0x464646;
      private static var lineH:Number = 2.2;
      private static var lineW:Number = 122;
      private static function hideLines():void
      {
         var bg:DisplayObject = inside.getChildAt(0);
         var b:Rectangle = bg.getBounds(inside);
         var bd:BitmapData = new BitmapData(Math.ceil(b.width), Math.ceil(b.height), false, 0);
         bd.draw(bg, new Matrix(1, 0, 0, 1, -b.x, -b.y));
         var cover:Shape = new Shape();
         var x:int = int(CX - b.x);
         var y:int = 60;
         var found:int = 0;
         while(y < 290 && y < bd.height - 2)
         {
            var base:uint = bd.getPixel(x, y - 3) & 0xFF;
            var px:uint = bd.getPixel(x, y) & 0xFF;
            if(px > base + 12)
            {
               var y1:int = y;
               while(y1 < bd.height - 1 && (bd.getPixel(x, y1) & 0xFF) > base + 12) y1++;
               var x0:int = x, x1:int = x;
               var ym:int = (y + y1) / 2;
               while(x0 > 1 && (bd.getPixel(x0, ym) & 0xFF) > base + 8) x0--;
               while(x1 < bd.width - 1 && (bd.getPixel(x1, ym) & 0xFF) > base + 8) x1++;
               if(found == 0) { lineColor = bd.getPixel(x, ym); lineH = Math.max(1.5, y1 - y); lineW = x1 - x0; }
               cover.graphics.beginFill(bd.getPixel(x, y - 3));
               cover.graphics.drawRect(b.x + x0 - 2, b.y + y - 2, (x1 - x0) + 4, (y1 - y) + 4);
               cover.graphics.endFill();
               found++;
               y = y1 + 3;
            }
            else y++;
         }
         bd.dispose();
         inside.addChildAt(cover, 1);
      }

      private static function separator(y:Number):void
      {
         var s:Shape = new Shape();
         s.graphics.beginFill(lineColor);
         s.graphics.drawRoundRect(CX - lineW / 2, y, lineW, lineH, lineH, lineH);
         s.graphics.endFill();
         inside.addChildAt(s, 2);
      }

      // ------------------------------------------------------------------ desplegable de idioma
      private static function makeLangHead(ref:MovieClip):Sprite
      {
         var sp:Sprite = new Sprite();
         for(var i:int = 0; i < ref.numChildren; i++)
         {
            var d:DisplayObject = ref.getChildAt(i);
            if(d is TextField) continue;
            var b:Rectangle = d.getBounds(ref);
            var bm:Bitmap = new Bitmap(snapshotIn(d, ref), "auto", true);
            bm.scaleX = bm.scaleY = 1 / SNAP; bm.x = b.x; bm.y = b.y;
            sp.addChild(bm);
         }
         var r:TextField = ref.label_txt;
         langLabel = new TextField();
         langLabel.embedFonts = true; langLabel.selectable = false; langLabel.mouseEnabled = false;
         langLabel.antiAliasType = r.antiAliasType; langLabel.gridFitType = r.gridFitType; langLabel.sharpness = r.sharpness; langLabel.thickness = r.thickness;
         langLabel.defaultTextFormat = r.defaultTextFormat;
         langLabel.x = r.x; langLabel.y = r.y; langLabel.width = r.width; langLabel.height = r.height;
         langLabel.text = JM.langName(JM.lang);
         sp.addChild(langLabel);
         sp.scaleX = ref.scaleX; sp.scaleY = ref.scaleY;
         sp.mouseChildren = false; sp.buttonMode = true; sp.useHandCursor = true;
         sp.addEventListener(MouseEvent.MOUSE_DOWN, openLang);
         return sp;
      }

      private static function snapshotIn(d:DisplayObject, parent:DisplayObject):BitmapData
      {
         var b:Rectangle = d.getBounds(parent);
         var bd:BitmapData = new BitmapData(Math.ceil(b.width * SNAP) + 2, Math.ceil(b.height * SNAP) + 2, true, 0);
         var m:Matrix = d.transform.matrix.clone();
         m.translate(-b.x, -b.y); m.scale(SNAP, SNAP);
         bd.draw(d, m, null, null, null, true);
         return bd;
      }

      private static function openLang(e:MouseEvent):void
      {
         if(pop != null || screen.isShowingDropdown) return;
         var g:Object = JM.game;
         g.soundManager.playSound("buttonclick.wav");
         pop = new (getDefinitionByName("app_settings_dropdown_popup") as Class)();
         pop.label_txt.text = JM.langName(JM.lang);
         var P:Class = getDefinitionByName("app_settings_dropdown_panel") as Class;
         var codes:Array = JM.langs.concat();
         codes.sort(function(a:String, b:String):int { return a == "es" ? -1 : (b == "es" ? 1 : (a < b ? -1 : 1)); });
         for(var i:int = 0; i < codes.length; i++)
         {
            var p:MovieClip = new P();
            p.buttonMode = true; p.mouseEnabled = true; p.mouseChildren = false;
            p.gotoAndStop(i % 2 == 0 ? 2 : 1);
            p.y = 25 + i * 23;
            p.label_txt.text = JM.langName(codes[i]);
            p.label_txt.mouseEnabled = false;
            p.whichType = codes[i];
            p.arrow.visible = codes[i] == JM.lang;
            p.hiliter.visible = false; p.hiliter.gotoAndStop(1);
            p.hitArea = p.hitclip; p.hitclip.mouseEnabled = false;
            p.addEventListener(MouseEvent.MOUSE_UP, chooseLang);
            p.addEventListener(MouseEvent.ROLL_OVER, overLang);
            p.addEventListener(MouseEvent.ROLL_OUT, outLang);
            pop.addChild(p);
            popParts.push(p);
         }
         pop.bottomcap.y = popParts[popParts.length - 1].y + 24;
         pop.bottomcap.gotoAndStop(codes.length % 2 == 0 ? 1 : 2);
         pop.scaleX = langHead.scaleX * inside.scaleX;
         pop.scaleY = langHead.scaleY * inside.scaleY;
         pop.x = langHead.x * inside.scaleX;
         pop.y = langHead.y * inside.scaleY;
         g.resizerClip.addChild(pop);
         pop.cover.x = 0 - pop.x; pop.cover.y = 0 - pop.y;
         pop.cover.addEventListener(MouseEvent.MOUSE_UP, closeLang);
         pop.covertop.addEventListener(MouseEvent.MOUSE_DOWN, closeLang);
      }

      private static function overLang(e:MouseEvent):void
      {
         for each(var p:MovieClip in popParts)
         {
            var on:Boolean = p == e.currentTarget;
            p.hiliter.visible = on;
            if(on) p.hiliter.gotoAndPlay(1); else p.hiliter.gotoAndStop(1);
         }
      }

      private static function outLang(e:MouseEvent):void
      {
         MovieClip(e.currentTarget).hiliter.visible = false;
         MovieClip(e.currentTarget).hiliter.gotoAndStop(1);
      }

      private static function chooseLang(e:MouseEvent):void
      {
         var code:String = MovieClip(e.currentTarget).whichType;
         closeLang();
         if(code != JM.lang)
         {
            JM.setLang(code);
            refreshTexts();
         }
      }

      /** Tras cambiar de idioma: etiquetas propias y las que el juego escribe por código. */
      public static function refreshTexts():void
      {
         try
         {
            if(langLabel != null) langLabel.text = JM.langName(JM.lang);
            for each(var ow:Object in own) { JM.setText([ow.tf, ow.en]); JM.refit(ow.tf); }
            if(inside != null) { placeMute(inside.soundfx, 150, 156); placeMute(inside.music, 330, 156); }
            if(screen != null && screen.clip != null)
            {
               var W:Object = getDefinitionByName("flipline.api.utils.WindowUtility");
               var S:Object = getDefinitionByName("flipline.api.utils.StringUtility");
               var Q:Object = getDefinitionByName("swordGame.data.GameQuality");
               JM.setText([inside.window_dropdown.label_txt, S.capitalize(W.getSizeLabel(W.currentSize), true)]);
               JM.setText([inside.quality_dropdown.label_txt, S.capitalize(Q.getQuality(), true)]);
            }
         }
         catch(e:Error) { JM.log("refresco: " + e.message); }
      }

      private static function closeLang(e:Event = null):void
      {
         if(pop == null) return;
         pop.cover.removeEventListener(MouseEvent.MOUSE_UP, closeLang);
         pop.covertop.removeEventListener(MouseEvent.MOUSE_DOWN, closeLang);
         for each(var p:MovieClip in popParts)
         {
            p.removeEventListener(MouseEvent.MOUSE_UP, chooseLang);
            p.removeEventListener(MouseEvent.ROLL_OVER, overLang);
            p.removeEventListener(MouseEvent.ROLL_OUT, outLang);
            p.hitArea = null;
         }
         if(pop.parent) pop.parent.removeChild(pop);
         pop = null; popParts = [];
      }

      // ------------------------------------------------------------------ deslizadores de grupo
      private static function find(k:Object):Object
      {
         for each(var s:Object in sliders) if(s.knob == k) return s;
         return null;
      }

      private static function onKnobOver(e:MouseEvent):void { if(drag == null) MovieClip(e.currentTarget).gotoAndStop(2); }
      private static function onKnobOut(e:MouseEvent):void { if(drag == null) MovieClip(e.currentTarget).gotoAndStop(1); }

      private static function onKnobDown(e:MouseEvent):void
      {
         if(drag != null) return;
         drag = find(e.currentTarget);
         if(drag == null) return;
         var g:Object = JM.game;
         g.soundManager.playSound("buttonclick.wav");
         g.addEventListener(MouseEvent.MOUSE_UP, onKnobUp);
         g.addEventListener("mouseLeaveWindow", onKnobUp);
         drag.knob.addEventListener(Event.ENTER_FRAME, onKnobMove);
         drag.knob.startDrag(false, new Rectangle(screen.volumeSliderStartX, drag.knob.y, screen.volumeSliderRange, 0));
      }

      private static function value(s:Object):Number
      {
         return Math.max(0, Math.min(1, (s.knob.x - screen.volumeSliderStartX) / screen.volumeSliderRange));
      }

      private static function onKnobMove(e:Event):void
      {
         if(drag == null) return;
         var v:Number = value(drag);
         if(Math.abs(v - JM.getVol(drag.id)) >= 0.025) JM.setVol(drag.id, v);
      }

      private static function onKnobUp(e:* = null):void
      {
         if(drag == null) return;
         var g:Object = JM.game;
         g.removeEventListener(MouseEvent.MOUSE_UP, onKnobUp);
         g.removeEventListener("mouseLeaveWindow", onKnobUp);
         drag.knob.removeEventListener(Event.ENTER_FRAME, onKnobMove);
         drag.knob.stopDrag();
         JM.setVol(drag.id, value(drag));
         JM.saveSettings();
         var id:String = drag.id;
         drag.knob.gotoAndStop(1);
         drag = null;
         // muestra de cómo queda el grupo
         var sample:String = JM.sampleOf(id);
         if(sample != null) g.soundManager.playSound(sample);
      }

      private static function onGone(e:Event):void
      {
         try
         {
            e.currentTarget.removeEventListener(Event.REMOVED_FROM_STAGE, onGone);
            e.currentTarget.removeEventListener(Event.ENTER_FRAME, watchQuit);
            modParts = []; quitShown = false;
            if(drag != null) onKnobUp();
            closeLang();
            for each(var s:Object in sliders)
            {
               s.knob.removeEventListener(MouseEvent.MOUSE_DOWN, onKnobDown);
               s.knob.removeEventListener(MouseEvent.ROLL_OVER, onKnobOver);
               s.knob.removeEventListener(MouseEvent.ROLL_OUT, onKnobOut);
            }
            sliders = []; extraLabels = [];
            if(langHead != null) langHead.removeEventListener(MouseEvent.MOUSE_DOWN, openLang);
            langHead = null; langLabel = null; noteTf = null; screen = null; inside = null;
         }
         catch(err:Error) {}
      }
   }
}
