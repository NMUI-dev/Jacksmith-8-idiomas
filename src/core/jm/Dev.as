package jm
{
   import flash.display.MovieClip;
   import flash.utils.getDefinitionByName;

   /** Órdenes de laboratorio (solo con Data/mods/dev.txt). No hace nada en la entrega. */
   public class Dev
   {
      public static var last:MovieClip = null;

      public static function run(p:Array):void
      {
         var g:Object = JM.game;
         try
         {
            if(p[0] == "call")
            {
               // call <ruta.de.objeto> <método> [args...]   p. ej.: call soundManager muteMusic
               var o:Object = g;
               if(p[1] != ".") for each(var k:String in String(p[1]).split(".")) o = o[k];
               var args:Array = p.slice(3);
               for(var i:int = 0; i < args.length; i++) if(!isNaN(Number(args[i]))) args[i] = Number(args[i]); else if(args[i] == "true") args[i] = true; else if(args[i] == "false") args[i] = false;
               var r:* = (o[p[2]] as Function).apply(o, args);
               JM.log("call " + p[1] + "." + p[2] + " -> " + r);
            }
            else if(p[0] == "set")
            {
               var o2:Object = g;
               var ks:Array = String(p[1]).split(".");
               for(var j:int = 0; j < ks.length - 1; j++) o2 = o2[ks[j]];
               var v:* = p[2];
               if(!isNaN(Number(v))) v = Number(v); else if(v == "true") v = true; else if(v == "false") v = false;
               o2[ks[ks.length - 1]] = v;
            }
            else if(p[0] == "get")
            {
               var o3:Object = g;
               for each(var k3:String in String(p[1]).split(".")) o3 = o3[k3];
               JM.log("get " + p[1] + " = " + o3);
            }
            else if(p[0] == "clip")
            {
               // clip <clase> [fotograma]  -> crea un clip del juego y lo pone encima (para ver historia, final...)
               if(last != null && last.parent != null) last.parent.removeChild(last);
               var C:Class = getDefinitionByName(p[1]) as Class;
               last = new C();
               g.gameOverlay.addChild(last);
               if(p.length > 2) last.gotoAndStop(int(p[2]));
               JM.log("clip " + p[1] + " fotogramas " + last.totalFrames);
            }
            else if(p[0] == "frame") { last.gotoAndStop(int(p[1])); }
            else if(p[0] == "play") { last.gotoAndPlay(p.length > 1 ? int(p[1]) : 1); }
            else if(p[0] == "rmclip") { if(last != null && last.parent != null) last.parent.removeChild(last); last = null; }
            else if(p[0] == "unlock") { g.showUnlockScreen(int(p[1])); }
            else if(p[0] == "vol")
            {
               JM.setVol(p[1], Number(p[2]));
               JM.saveSettings();
            }
         }
         catch(e:Error) { JM.log("dev " + p.join(" ") + ": " + e.message); }
      }
   }
}
