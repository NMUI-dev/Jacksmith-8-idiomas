package jm
{
   import flash.display.DisplayObject;
   import flash.display.DisplayObjectContainer;
   import flash.display.Loader;
   import flash.display.SimpleButton;
   import flash.display.Stage;
   import flash.events.Event;
   import flash.geom.Point;
   import flash.geom.Rectangle;
   import flash.media.SoundChannel;
   import flash.media.SoundTransform;
   import flash.net.SharedObject;
   import flash.net.URLRequest;
   import flash.system.ApplicationDomain;
   import flash.system.LoaderContext;
   import flash.text.TextField;
   import flash.text.TextFormat;
   import flash.utils.Dictionary;
   import flash.utils.getDefinitionByName;

   /**
    * Núcleo de mods de Jacksmith (capa única y compartida por todos los mods).
    *  - Idiomas: tablas JSON en Data/mods/<mod>/lang/<idioma>.json, se traducen los textos al mostrarlos.
    *  - Ajustes guardados (idioma, volúmenes y lo que registren otros mods) en el SharedObject "JacksmithMods".
    *  - Volumen separado de música y efectos.
    *  - Registro de mods: cada carpeta Data/mods/<mod>/ puede traer mod.json, lang/*.json y plugin.swf.
    */
   public class JM
   {
      public static const VERSION:String = "1.0.0";

      public static var game:Object = null;          // GameModule
      public static var stage:Stage = null;
      public static var dev:Boolean = false;          // existe Data/mods/dev.txt (solo laboratorio)
      public static var mods:Array = [];              // [{id, dir, info}]
      public static var plugins:Array = [];           // objetos raíz de los plugin.swf cargados
      public static var settings:Object = {};         // ajustes guardados (los mods pueden añadir claves propias)

      // ---------- idioma ----------
      public static var lang:String = "es";
      public static var langs:Array = ["en"];
      public static var langNames:Object = {"en":"English"};
      private static var exact:Object = {};
      private static var lower:Object = {};
      private static var patterns:Array = [];
      private static var cache:Object = {};
      private static var cacheN:int = 0;
      private static var reverse:Object = {};          // clave del texto traducido -> texto inglés (para cambiar de idioma en caliente)
      private static var missing:Object = {};
      private static var orig:Dictionary = new Dictionary(true);   // TextField -> {size, wrap, src}
      private static var seen:Dictionary = new Dictionary(true);   // TextField -> último texto visto
      private static var frame:int = 0;

      // ---------- volumen ----------
      public static var groups:Array = [];            // [{id, en, def, sample}] (Data/mods/*/sonidos.json)
      private static var soundMap:Object = {};        // id de sonido -> grupo
      private static var prefixes:Array = [];         // [[prefijo, grupo]]
      public static var vols:Object = {};             // grupo -> posición del deslizador 0..1
      private static var gains:Object = {};           // grupo -> ganancia real (curva cuadrática)
      public static var musicGain:Number = 0.25;      // ganancia de las pistas de música (la leen los parches)
      private static var chanGroup:Dictionary = new Dictionary(true);   // SoundChannel -> grupo

      public static var firstRun:Boolean = false;
      private static var pickShown:Boolean = false;
      private static var langNamesEn:Object = {"en":"English"};
      private static var idiomas:Object = {};

      private static var booted:Boolean = false;
      private static var so:SharedObject = null;
      public static var hooks:Object = {};            // nombre -> [funciones]; ver on()/emit()

      // =====================================================================================
      //  Arranque
      // =====================================================================================
      public static function boot():void
      {
         if(booted) return;
         booted = true;
         try { scanMods(); } catch(e2:Error) { log("mods: " + e2.message); }
         try { loadSettings(); } catch(e:Error) { log("ajustes: " + e.message); }
         try { loadLang(); } catch(e3:Error) { log("idioma: " + e3.message); }
      }

      /** Lo llama GameModule.initGame() (parche del núcleo). */
      public static function init(g:Object):void
      {
         boot();
         game = g;
         try
         {
            stage = g.stage;
            stage.addEventListener(Event.ADDED_TO_STAGE, onAdded, true);
            stage.addEventListener(Event.ENTER_FRAME, onFrame);
         }
         catch(e:Error) { log("init: " + e.message); }
         loadPlugins();
         emit("init", g);
      }

      // =====================================================================================
      //  Ajustes guardados
      // =====================================================================================
      private static function loadSettings():void
      {
         so = SharedObject.getLocal("JacksmithMods", "/");
         if(so.data.settings != null) settings = so.data.settings;
         if(settings.lang != null) lang = String(settings.lang); else firstRun = true;
         if(langs.indexOf(lang) == -1) lang = "en";
         var sv:Object = settings.vol != null ? settings.vol : {};
         for each(var g:Object in groups)
         {
            var v:Number = sv[g.id] != null ? Number(sv[g.id]) : Number(g.def);
            vols[g.id] = clamp(v);
         }
         updateGains();
      }

      public static function saveSettings():void
      {
         try
         {
            settings.lang = lang;
            settings.vol = vols;
            if(so == null) so = SharedObject.getLocal("JacksmithMods", "/");
            so.data.settings = settings;
            so.flush();
         }
         catch(e:Error) { log("guardar: " + e.message); }
      }

      public static function getSetting(k:String, def:* = null):*
      {
         boot();
         return settings[k] === undefined ? def : settings[k];
      }

      public static function setSetting(k:String, v:*):void
      {
         boot();
         settings[k] = v;
         saveSettings();
      }

      // =====================================================================================
      //  Mods: carpetas Data/mods/<mod>/
      // =====================================================================================
      private static function fileClass():Class { return getDefinitionByName("flash.filesystem.File") as Class; }

      public static function readText(f:Object):String
      {
         var FS:Class = getDefinitionByName("flash.filesystem.FileStream") as Class;
         var s:Object = new FS();
         s.open(f, "read");
         var t:String = s.readUTFBytes(s.bytesAvailable);
         s.close();
         if(t.length > 0 && t.charCodeAt(0) == 0xFEFF) t = t.substr(1);
         return t;
      }

      private static function scanMods():void
      {
         var F:Class = fileClass();
         var root:Object = F.applicationDirectory.resolvePath("Data/mods");
         mods = [];
         if(!root.exists) return;
         dev = root.resolvePath("dev.txt").exists;
         var list:Array = root.getDirectoryListing();
         list.sortOn("name");
         for each(var d:Object in list)
         {
            if(!d.isDirectory) continue;
            var info:Object = {};
            var mf:Object = d.resolvePath("mod.json");
            if(mf.exists)
            {
               try { info = JSON.parse(readText(mf)); } catch(e:Error) { log(d.name + "/mod.json: " + e.message); }
            }
            mods.push({id:d.name, dir:d, info:info});
            try { loadSounds(d); } catch(es:Error) { log(d.name + "/sonidos.json: " + es.message); }
            var ld:Object = d.resolvePath("lang");
            if(ld.exists && ld.isDirectory)
            {
               for each(var lf:Object in ld.getDirectoryListing())
               {
                  var n:String = lf.name;
                  if(n.substr(n.length - 5).toLowerCase() == ".json")
                  {
                     var code:String = n.substr(0, n.length - 5);
                     if(langs.indexOf(code) == -1) langs.push(code);
                  }
               }
            }
         }
      }

      private static function loadSounds(d:Object):void
      {
         var f:Object = d.resolvePath("sonidos.json");
         if(!f.exists) return;
         var o:Object = JSON.parse(readText(f));
         for each(var g:Object in o.grupos)
         {
            var found:Boolean = false;
            for(var i:int = 0; i < groups.length; i++) if(groups[i].id == g.id) { groups[i] = g; found = true; }
            if(!found) groups.push(g);
         }
         for(var k:String in o.sonidos)
         {
            if(k.charAt(k.length - 1) == "*") prefixes.push([k.substr(0, k.length - 1), o.sonidos[k]]);
            else soundMap[k] = o.sonidos[k];
         }
         prefixes.sort(function(a:Array, b:Array):int { return b[0].length - a[0].length; });
      }

      private static function loadPlugins():void
      {
         for each(var m:Object in mods)
         {
            try
            {
               var pf:Object = m.dir.resolvePath("plugin.swf");
               if(!pf.exists) continue;
               var ld:Loader = new Loader();
               var ctx:LoaderContext = new LoaderContext(false, ApplicationDomain.currentDomain);
               try { ctx["allowCodeImport"] = true; } catch(e0:Error) {}
               ld.contentLoaderInfo.addEventListener(Event.COMPLETE, onPlugin);
               ld.load(new URLRequest(pf.url), ctx);
            }
            catch(e:Error) { log("plugin " + m.id + ": " + e.message); }
         }
      }

      private static function onPlugin(e:Event):void
      {
         try
         {
            var c:Object = e.target.content;
            plugins.push(c);
            if(c.hasOwnProperty("jmInit")) c.jmInit(JM);
         }
         catch(err:Error) { log("plugin init: " + err.message); }
      }

      /** Ganchos sencillos para otros mods: JM.on("options", f) ; el núcleo llama emit("options", pantalla). */
      public static function on(name:String, f:Function):void
      {
         if(hooks[name] == null) hooks[name] = [];
         hooks[name].push(f);
      }

      public static function emit(name:String, arg:* = null):void
      {
         var a:Array = hooks[name];
         if(a == null) return;
         for each(var f:Function in a)
         {
            try { f(arg); } catch(e:Error) { log("gancho " + name + ": " + e.message); }
         }
      }

      // =====================================================================================
      //  Idioma
      // =====================================================================================
      public static function key(s:String):String
      {
         return s.replace(/[\s ]+/g, "").replace(/[‘’]/g, "'");
      }

      public static function loadLang():void
      {
         exact = {}; lower = {}; patterns = []; cache = {}; cacheN = 0; reverse = {}; idiomas = {};
         for each(var m:Object in mods)
         {
            var ld:Object = m.dir.resolvePath("lang");
            if(!ld.exists) continue;
            for each(var code:String in langs)
            {
               if(code == "en") continue;
               if(code != lang && langNames[code] != null) continue;      // solo hace falta su nombre
               var f:Object = ld.resolvePath(code + ".json");
               if(!f.exists) continue;
               try
               {
                  var o:Object = JSON.parse(readText(f));
                  if(o.nombre != null) langNames[code] = String(o.nombre);
                  if(o.nombre_en != null) langNamesEn[code] = String(o.nombre_en);
                  else if(langNames[code] == null) langNames[code] = code;
                  if(code == lang) addTable(o);
               }
               catch(e:Error) { log(m.id + "/lang/" + code + ".json: " + e.message); if(langNames[code] == null) langNames[code] = code; }
            }
         }
      }

      private static function addTable(o:Object):void
      {
         var k:String;
         if(o.idiomas != null) for(k in o.idiomas) idiomas[k] = String(o.idiomas[k]);
         if(o.textos != null)
         {
            for(k in o.textos)
            {
               var kk:String = key(k);
               var v:String = String(o.textos[k]);
               exact[kk] = v;
               lower[kk.toLowerCase()] = v;
               reverse[key(v)] = k;
            }
         }
         if(o.patrones != null)
         {
            for each(var p:Array in o.patrones)
            {
               try { patterns.push([new RegExp(p[0]), String(p[1])]); } catch(e:Error) { log("patrón " + p[0] + ": " + e.message); }
            }
         }
      }

      /** Nombre de un idioma escrito en ese mismo idioma (日本語, Русский): el que trae su tabla en «nombre». */
      public static function ownName(code:String):String
      {
         boot();
         if(code == "en") return "English";
         return langNames[code] != null ? String(langNames[code]) : code;
      }

      /** Nombre de un idioma escrito en el idioma activo («Español / Inglés» o «Spanish / English»). */
      public static function langName(code:String):String
      {
         boot();
         if(idiomas[code] != null) return idiomas[code];
         if(lang == "en" && langNamesEn[code] != null) return langNamesEn[code];
         if(langNames[code] != null) return langNames[code];
         return code;
      }

      public static function refit(tf:TextField):void
      {
         var o:Object = info(tf);
         var f:TextFormat = new TextFormat(); f.size = o.size;
         try { if(tf.length > 0) tf.setTextFormat(f); } catch(e:Error) {}
         fit(tf, o);
      }

      public static function setLang(code:String):void
      {
         if(code == lang || langs.indexOf(code) == -1) return;
         var old:String = lang;
         // 1) devolver al inglés los campos visibles que estén traducidos
         var fields:Array = [];
         if(stage != null) collect(stage, fields);
         var tf:TextField;
         for each(tf in fields)
         {
            var o:Object = orig[tf];
            if(o != null && o.src != null && key(tf.text) == key(String(o.dst))) { rawSet(tf, o.src, o); }
         }
         lang = code;
         loadLang();
         seen = new Dictionary(true);
         for each(tf in fields) fix(tf);
         for(var ac:Object in arts) { try { fixArt(ac as DisplayObjectContainer); } catch(ea:Error) {} }
         saveSettings();
         try { Options.refreshTexts(); } catch(eo:Error) {}
         emit("lang", code);
      }

      private static function collect(c:DisplayObjectContainer, out:Array):void
      {
         var n:int = c.numChildren;
         for(var i:int = 0; i < n; i++)
         {
            var d:DisplayObject = null;
            try { d = c.getChildAt(i); } catch(e:Error) { continue; }
            if(d is TextField) { if(out.indexOf(d) == -1) out.push(d); }
            else if(d is SimpleButton) buttonFields(d as SimpleButton, out);
            else if(d is DisplayObjectContainer) { artCheck(d as DisplayObjectContainer); collect(d as DisplayObjectContainer, out); }
         }
      }

      /** Traduce un valor si es una cadena conocida; si no, lo devuelve igual. */
      public static function t(v:*):*
      {
         if(!(v is String)) return v;
         if(!booted) boot();
         if(lang == "en") return v;
         var s:String = v;
         if(s.length < 2) return v;
         var c:* = cache[s];
         if(c !== undefined) return c;
         var r:String = null;
         if(/[A-Za-z]/.test(s))
         {
            var k:String = key(s);
            r = exact[k];
            if(r == null)
            {
               r = lower[k.toLowerCase()];
               if(r != null && s == s.toUpperCase() && s != s.toLowerCase()) r = r.toUpperCase();
            }
            if(r == null) r = byPattern(s);
            if(r == null)
            {
               if(dev && missing[s] == null && reverse[k] == null) { missing[s] = 1; devAppend("jm_missing.txt", JSON.stringify(s) + "\n"); }
            }
            else
            {
               var a:Array = s.match(/^[\s ]+/);
               var b:Array = s.match(/[\s ]+$/);
               if(a != null) r = a[0] + r;
               if(b != null) r = r + b[0];
            }
         }
         if(r == null) r = s;
         if(cacheN > 4000) { cache = {}; cacheN = 0; }
         cache[s] = r; cacheN++;
         return r;
      }

      private static function byPattern(s:String):String
      {
         var n:String = s.replace(/[\s ]+/g, " ").replace(/^ | $/g, "");
         for each(var p:Array in patterns)
         {
            var m:Object = (p[0] as RegExp).exec(n);
            if(m == null) continue;
            var out:String = p[1];
            for(var i:int = 1; i < m.length; i++)
            {
               var g:String = m[i] == null ? "" : String(m[i]);
               out = out.split("{" + i + "}").join(String(t(g)));
               out = out.split("{" + i + "l}").join(String(t(g)).toLowerCase());
               out = out.split("$" + i).join(g);
            }
            return out;
         }
         return null;
      }

      /** Parche de «obj.text = valor» (la pila trae [obj, valor] empaquetados en un Array). */
      public static function setText(a:Array):void
      {
         var o:* = a[0];
         var v:* = a[1];
         if((o is TextField) && (v is String) && lang != "en")
         {
            var tf:TextField = o;
            if(tf.type == "input") { tf.text = v; return; }
            var r:String = t(v);
            var oo:Object = info(tf);
            if(r === v) { restoreWrap(tf, oo); tf.text = v; oo.src = null; }
            else { oo.src = v; oo.dst = r; oo.html = false; tf.text = r; fit(tf, oo); }
            seen[tf] = tf.text;
            return;
         }
         o.text = v;
      }

      /** Parche de «obj.htmlText = valor». */
      public static function setHtml(a:Array):void
      {
         var o:* = a[0];
         var v:* = a[1];
         if((o is TextField) && (v is String) && lang != "en")
         {
            var tf:TextField = o;
            var s:String = v;
            var plain:String = s.replace(/<[^>]+>/g, "");
            var r:String = t(plain);
            var oo:Object = info(tf);
            if(r === plain || s.indexOf(plain) == -1)
            {
               // HTML con formato intercalado: traducir los tramos de texto entre etiquetas
               var changed:Boolean = false;
               var out:String = s.replace(/>([^<>]+)</g, function():String {
                  var seg:String = arguments[1]; var tr:String = t(seg);
                  if(tr !== seg) changed = true;
                  return ">" + tr + "<";
               });
               if(r !== plain && !changed)
               {
                  // la frase entera tiene traducción pero va partida por etiquetas: se pone sin formato interior
                  oo.src = plain; oo.dst = r; oo.html = false; tf.text = r; fit(tf, oo); seen[tf] = tf.text; return;
               }
               restoreWrap(tf, oo);
               tf.htmlText = out;
               if(changed) { oo.src = null; fit(tf, oo, true); }
               seen[tf] = tf.text;
               return;
            }
            tf.htmlText = s.split(plain).join(r);
            oo.src = null;
            fit(tf, oo, true);
            seen[tf] = tf.text;
            return;
         }
         o.htmlText = v;
      }

      private static function info(tf:TextField):Object
      {
         var o:Object = orig[tf];
         if(o == null)
         {
            var sz:Number = 12;
            try { sz = Number(tf.defaultTextFormat.size); } catch(e:Error) {}
            if(isNaN(sz) || sz <= 0) sz = 12;
            o = {size:sz, wrap:tf.wordWrap, src:null, dst:null};
            orig[tf] = o;
         }
         return o;
      }

      private static function restoreWrap(tf:TextField, o:Object):void
      {
         if(tf.wordWrap != o.wrap) tf.wordWrap = o.wrap;
      }

      /** Centros (en coordenadas del padre) de los huecos de 4 o más espacios seguidos del texto. */
      private static function gapCenters(tf:TextField):Array
      {
         var out:Array = [];
         try
         {
            var s:String = tf.text;
            var rx:RegExp = /[ \u00A0]{4,}/g;
            var m:Object;
            while((m = rx.exec(s)) != null)
            {
               var i:int = m.index + int(m[0].length / 2);
               var r:Rectangle = tf.getCharBoundaries(i);
               if(r == null) r = tf.getCharBoundaries(m.index);
               if(r != null) out.push(new Point(tf.x + (r.x + r.width / 2) * tf.scaleX, tf.y + (r.y + r.height / 2) * tf.scaleY));
               else out.push(null);
            }
         }
         catch(e:Error) {}
         return out;
      }

      private static var pendingIcons:Array = [];

      private static function moveIcons(tf:TextField, o:Object, before:Array):void
      {
         try
         {
            var after:Array = gapCenters(tf);
            var par:DisplayObjectContainer = tf.parent;
            if(par == null) return;
            o.moved = [];
            for(var k:int = 0; k < before.length && k < after.length; k++)
            {
               var a:Point = before[k]; var b:Point = after[k];
               if(a == null || b == null) continue;
               if(dev) { var dbg:String = "iconos «" + tf.text.substr(0, 18) + "» a=" + int(a.x) + "," + int(a.y) + " b=" + int(b.x) + "," + int(b.y) + " :"; for(var q:int = 0; q < par.numChildren; q++) { var dq:DisplayObject = par.getChildAt(q); if(dq == tf || dq is TextField) continue; var rq:Rectangle = dq.getBounds(par); if(Math.abs(rq.y + rq.height / 2 - a.y) < 60) dbg += " [" + int(rq.x) + "," + int(rq.y) + " " + int(rq.width) + "x" + int(rq.height) + "]"; } log(dbg); }
               var best:DisplayObject = null; var bd:Number = 22;
               for(var i:int = 0; i < par.numChildren; i++)
               {
                  var d:DisplayObject = par.getChildAt(i);
                  if(d == null || d == tf || d is TextField || !d.visible) continue;
                  var r:Rectangle = d.getBounds(par);
                  if(r.width > 60 || r.height > 60 || r.width < 3) continue;
                  var dist:Number = Math.abs(r.x + r.width / 2 - a.x) + Math.abs(r.y + r.height / 2 - a.y);
                  if(dist < bd) { bd = dist; best = d; }
               }
               if(best != null)
               {
                  // un mismo icono puede quedar entre dos huecos (tecla «D» con espacios a los lados): se mueve UNA vez, la media
                  var dx:Number = b.x - a.x; var dy:Number = b.y - a.y;
                  var ya:Object = null;
                  for each(var m0:Object in o.moved) if(m0.d == best) ya = m0;
                  if(ya == null) o.moved.push({d:best, dx:dx, dy:dy, n:1});
                  else { ya.dx = (ya.dx * ya.n + dx) / (ya.n + 1); ya.dy = (ya.dy * ya.n + dy) / (ya.n + 1); ya.n++; }
               }
            }
            for each(var m1:Object in o.moved) { m1.d.x += m1.dx; m1.d.y += m1.dy; }
         }
         catch(e:Error) { log("iconos: " + e.message); }
      }

      private static function rawSet(tf:TextField, s:String, o:Object):void
      {
         if(o.moved != null)
         {
            for each(var mv:Object in o.moved) { try { mv.d.x -= mv.dx; mv.d.y -= mv.dy; } catch(em:Error) {} }
            o.moved = null;
         }
         var f:TextFormat = null;
         try { if(tf.length > 0 && tf.maxChars != 7777) f = tf.getTextFormat(0, 1); } catch(e:Error) {}
         restoreWrap(tf, o);
         if(o.dy != null && Number(o.dy) != 0) { tf.y -= Number(o.dy); o.dy = 0; }
         tf.text = s;
         if(f != null)
         {
            f.size = o.size;
            if(o.mg != null && Number(o.mg) > 0) { f.leftMargin = tf.defaultTextFormat.leftMargin; f.rightMargin = tf.defaultTextFormat.rightMargin; }
            try { tf.setTextFormat(f); } catch(e2:Error) {}
         }
         o.mg = 0;
         o.src = null;
         pendingKeys.push(tf);
      }

      // ---------- tecla dibujada: «Pulsa   D   para...» lleva detrás de la letra suelta un recuadro (la tecla).
      // La letra va en negro (como en el original) y el recuadro se centra bajo ella: nada tapa las palabras vecinas.
      private static var pendingKeys:Array = [];
      private static var keyFields:Dictionary = new Dictionary(true);
      private static const KEYRX:RegExp = /[  ]{2,}\S[  ]{2,}/;

      private static function keyCap(tf:TextField):void
      {
         try
         {
            var par:DisplayObjectContainer = tf.parent;
            if(par == null) return;
            var m:Object = /[  ]{2,}(\S)[  ]{2,}/.exec(tf.text);
            if(m == null) return;
            var i:int = m.index + String(m[0]).indexOf(m[1]);
            var r:Rectangle = tf.getCharBoundaries(i);
            if(r == null) return;
            var pc:Point = par.globalToLocal(tf.localToGlobal(new Point(r.x + r.width / 2, r.y + r.height / 2)));
            var cx:Number = pc.x; var cy:Number = pc.y;
            var best:DisplayObject = null; var bd:Number = 400;
            for(var k:int = 0; k < par.numChildren; k++)
            {
               var d:DisplayObject = par.getChildAt(k);
               if(d == null || d == tf || d is TextField || !d.visible) continue;
               var b:Rectangle = d.getBounds(par);
               if(b.width > 60 || b.height > 60 || b.width < 6) continue;
               if(Math.abs(b.y + b.height / 2 - cy) > 14) continue;
               var dist:Number = Math.abs(b.x + b.width / 2 - cx);
               if(dist < bd) { bd = dist; best = d; }
            }
            if(best == null) return;
            var bb:Rectangle = best.getBounds(par);
            if(Math.abs(cx - (bb.x + bb.width / 2)) > 0.5) best.x += cx - (bb.x + bb.width / 2);
            var kf:TextFormat = new TextFormat(); kf.color = 0x000000;
            tf.setTextFormat(kf, i, i + 1);
         }
         catch(e:Error) { log("tecla: " + e.message); }
      }

      /** Campo recién aparecido (texto fijo de la línea de tiempo) o cambiado sin pasar por setText. */
      public static function fix(tf:TextField):void
      {
         try
         {
            if(tf.type == "input") return;
            var s:String = tf.text;
            seen[tf] = s;
            if(s.length > 6 && s.length < 80 && KEYRX.test(s)) keyFields[tf] = true;
            if(lang == "en" || s.length < 2) return;
            var r:String = t(s);
            if(r === s) return;
            var o:Object = info(tf);
            var f:TextFormat = null;
            try { f = tf.getTextFormat(0, 1); } catch(e:Error) {}
            if(f != null && f.size != null) o.fsize = Number(f.size); else o.fsize = o.size;
            o.src = s; o.dst = r;
            var gaps0:Array = gapCenters(tf);
            if(tf.maxChars == 7777)
            {
               // era texto estático: el juego lo destapa renglón a renglón con máscaras del ancho del original
               var lw:Array = []; var asc0:Number = 0; var lh0:Number = 0;
               try
               {
                  for(var li:int = 0; li < tf.numLines; li++) lw.push(tf.getLineMetrics(li).width);
                  asc0 = tf.getLineMetrics(0).ascent; lh0 = tf.getLineMetrics(0).height;
               }
               catch(el:Error) {}
               tf.text = r;
               fitStatic(tf, o, lw, asc0, lh0);
               seen[tf] = tf.text;
               pendingKeys.push(tf);
               if(gaps0.length > 0) pendingIcons.push([tf, o, gaps0]);     // también los textos que eran estáticos llevan iconos en huecos
               return;
            }
            var engW:Number = 0;
            try
            {
               var lce:Number = s.charCodeAt(s.length - 1);
               var realLines:int = tf.numLines - ((lce == 13 || lce == 10) ? 1 : 0);
               if(!tf.wordWrap && realLines > 1)
                  for(var le:int = 0; le < tf.numLines; le++) engW = Math.max(engW, tf.getLineMetrics(le).width);
            }
            catch(ew:Error) {}
            tf.text = r;
            if(f != null) { try { tf.setTextFormat(f); } catch(e2:Error) {} }
            o.mg = 0;
            if(engW > 20)
            {
               var boxW:Number = tf.width / Math.abs(tf.scaleX == 0 ? 1 : tf.scaleX) - 4;
               var extra:Number = boxW - engW * 1.03;
               if(extra > 6)
               {
                  var fm:TextFormat = new TextFormat();
                  var al:String = (f != null && f.align != null) ? String(f.align) : "left";
                  if(al == "center") { fm.leftMargin = extra / 2; fm.rightMargin = extra / 2; }
                  else if(al == "right") fm.leftMargin = extra;
                  else fm.rightMargin = extra;
                  try { tf.setTextFormat(fm); o.mg = extra; } catch(e3:Error) {}
               }
            }
            fit(tf, o, false, o.fsize);
            if(gaps0.length > 0) pendingIcons.push([tf, o, gaps0]);      // los iconos vecinos aún no existen: se recolocan en el fotograma siguiente
            seen[tf] = tf.text;
         }
         catch(err:Error) { log("fix: " + err.message); }
      }

      /** Texto que era estático: cada renglón traducido debe caber en el ancho de SU renglón original,
       *  y los renglones no se mueven de sitio (se compensa el interlineado y la subida de la letra). */
      private static function fitStatic(tf:TextField, o:Object, lw:Array, asc0:Number, lh0:Number):void
      {
         try
         {
            var base:Number = Number(tf.defaultTextFormat.size);
            var lead0:Number = Number(tf.defaultTextFormat.leading);
            if(isNaN(lead0)) lead0 = 0;
            var maxw:Number = 0;
            for each(var x:Number in lw) if(x > maxw) maxw = x;
            var sz:Number = base; var min:Number = Math.max(6, base * 0.5); var guard:int = 0;
            while(guard++ < 60)
            {
               var over:Boolean = false;
               for(var i:int = 0; i < tf.numLines; i++)
               {
                  var lim:Number = (i < lw.length && lw[i] > 4) ? lw[i] : maxw;
                  var wi:Number = tf.getLineMetrics(i).width;
                  if(wi > 0.5 && wi > lim + 0.5) { over = true; break; }
               }
               if(!over || sz <= min) break;
               sz = Math.max(min, Math.floor(sz * 0.97 * 4) / 4);
               var f:TextFormat = new TextFormat();
               f.size = sz;
               tf.setTextFormat(f);
               var f2:TextFormat = new TextFormat();
               f2.leading = lead0 + (lh0 - tf.getLineMetrics(0).height) + (Number(tf.getTextFormat(0, 1).leading) - lead0);
               tf.setTextFormat(f2);
            }
            var dy:Number = (sz < base) ? (asc0 - tf.getLineMetrics(0).ascent) * Math.abs(tf.scaleY) : 0;
            var old:Number = o.dy == null ? 0 : Number(o.dy);
            if(dy != old) { tf.y = tf.y - old + dy; o.dy = dy; }
            if(dev && sz <= min) devAppend("jm_overflow.txt", JSON.stringify(tf.text) + " (estático)\n");
         }
         catch(e:Error) { log("fitStatic: " + e.message); }
      }

      /** Encoge la letra lo justo para que el texto quepa en su caja (nunca desborda). */
      public static function fit(tf:TextField, o:Object, keepFormats:Boolean = false, baseSize:Number = NaN):void
      {
         try
         {
            if(tf.autoSize != "none") return;
            var s:String = tf.text;
            if(s.length == 0) return;
            var multi:Boolean = tf.multiline || tf.wordWrap || o.wrap || s.indexOf("\r") >= 0 || s.indexOf("\n") >= 0;
            var w:Number = tf.width / Math.abs(tf.scaleX == 0 ? 1 : tf.scaleX);
            var h:Number = tf.height / Math.abs(tf.scaleY == 0 ? 1 : tf.scaleY);
            var base:Number = isNaN(baseSize) ? o.size : baseSize;
            try
            {
               var df:TextFormat = tf.defaultTextFormat;
               var mg:Number = Number(df.leftMargin) + Number(df.rightMargin);
               if(o.mg != null && Number(o.mg) > 0) mg = Number(o.mg);
               if(!isNaN(mg) && mg > 0 && mg < w * 0.7) w -= mg;
            }
            catch(em:Error) {}
            if(multi && !tf.wordWrap && (tf.multiline || o.srcMulti) && tf.maxChars != 7777) tf.wordWrap = true;
            var words:int = s.replace(/^\s+|\s+$/g, "").split(/\s+/).length;
            var last:String = s.charAt(s.length - 1);
            var lc:Number = last.charCodeAt(0);
            var trail:int = (lc == 13 || lc == 10) ? 1 : 0;
            var sz:Number = base;
            var min:Number = Math.max(6, base * 0.55);
            var guard:int = 0;
            while(guard++ < 40)
            {
               var over:Boolean;
               if(tf.wordWrap) over = (tf.numLines > 1 && tf.textHeight > h + 1) || (tf.textWidth + 4 > w + 1.5) || (tf.numLines - trail > words) || (tf.maxScrollV > 1 && tf.numLines - trail > 1);
               else over = (tf.textWidth + 4 > w + 1.5) || (tf.numLines > 1 && tf.textHeight > h + 1);
               if(!over || sz <= min) break;
               sz = Math.max(min, Math.floor(sz * 0.95 * 2) / 2);
               var f:TextFormat = new TextFormat();
               f.size = sz;
               tf.setTextFormat(f);
            }
            // una sola línea encogida: se baja lo justo para que siga centrada en vertical
            var dy:Number = (tf.numLines - trail <= 1 && sz < base) ? (base - sz) * 0.6 * Math.abs(tf.scaleY) : 0;
            var old:Number = o.dy == null ? 0 : Number(o.dy);
            if(dy != old) { tf.y = tf.y - old + dy; o.dy = dy; }
            if(dev && sz <= min && guard > 1) devAppend("jm_overflow.txt", JSON.stringify(s) + " caja " + int(w) + "x" + int(h) + "\n");
         }
         catch(e:Error) { log("fit: " + e.message); }
      }

      private static function onAdded(e:Event):void
      {
         var o:Object = e.target;
         if(o is TextField)
         {
            var tf:TextField = o as TextField;
            if(tf.maxChars == 7777) tf.mouseEnabled = false;      // era texto estático: que no estorbe al ratón
            fix(tf);
         }
         else if(o is SimpleButton) fixButton(o as SimpleButton);
         else if(o is DisplayObjectContainer) artCheck(o as DisplayObjectContainer);
      }

      // ---------- rótulos dibujados por idioma (pieza 40): sprite con hijos «jm_en» y «jm_<idioma>_N»
      private static var arts:Dictionary = new Dictionary(true);

      private static function artCheck(c:DisplayObjectContainer):void
      {
         try
         {
            if(c.numChildren >= 2 && c.getChildAt(0).name == "jm_en")
            {
               arts[c] = true;
               c.mouseChildren = false;          // antes era un dibujo: que el ratón lo atraviese igual
               if(c is flash.display.InteractiveObject) (c as flash.display.InteractiveObject).mouseEnabled = false;
               fixArt(c);
            }
         }
         catch(e:Error) {}
      }

      public static function fixArt(c:DisplayObjectContainer):void
      {
         var pre:String = "jm_" + lang + "_";
         var has:Boolean = false;
         for(var i:int = 1; i < c.numChildren; i++)
         {
            var d:DisplayObject = c.getChildAt(i);
            var on:Boolean = d.name.indexOf(pre) == 0;
            d.visible = on;
            if(on) has = true;
         }
         c.getChildAt(0).visible = !has;
      }

      /** Los textos de un botón viven en sus estados, fuera de la lista de visualización. */
      public static function fixButton(b:SimpleButton):void
      {
         try
         {
            var a:Array = [];
            buttonFields(b, a);
            for each(var tf:TextField in a) fix(tf);
         }
         catch(e:Error) {}
      }

      private static function buttonFields(b:SimpleButton, out:Array):void
      {
         for each(var st:DisplayObject in [b.upState, b.overState, b.downState])
         {
            if(st is TextField) { if(out.indexOf(st) == -1) out.push(st); }
            else if(st is DisplayObjectContainer) { artCheck(st as DisplayObjectContainer); collect(st as DisplayObjectContainer, out); }
         }
      }

      private static function onFrame(e:Event):void
      {
         frame++;
         if(pendingIcons.length > 0)
         {
            var pi:Array = pendingIcons; pendingIcons = [];
            for each(var pe:Array in pi) { if(pe[1].src != null) moveIcons(pe[0], pe[1], pe[2]); }
         }
         if(pendingKeys.length > 0)
         {
            var pk:Array = pendingKeys; pendingKeys = [];
            for each(var kt:TextField in pk) keyCap(kt);
         }
         if(frame % 10 == 0)
         {
            for(var kf2:Object in keyFields) { if((kf2 as TextField).stage != null) keyCap(kf2 as TextField); }
         }
         if(frame % 5 == 0 && lang != "en")
         {
            try { sweep(stage); } catch(err:Error) {}
         }
         if(dev && frame % 15 == 0) devPoll();
         if(firstRun && !pickShown)
         {
            try
            {
               if(game != null && game.resizerClip != null && game.resizerClip.stage != null) { pickShown = true; LangPick.show(); }
            }
            catch(e2:Error) { pickShown = true; log("idioma inicial: " + e2.message); }
         }
      }

      private static function sweep(c:DisplayObjectContainer):void
      {
         var n:int = c.numChildren;
         for(var i:int = 0; i < n; i++)
         {
            var d:DisplayObject = c.getChildAt(i);
            if(d is TextField)
            {
               var tf:TextField = d as TextField;
               if(seen[tf] !== tf.text) fix(tf);
            }
            else if(d is DisplayObjectContainer && d.visible) sweep(d as DisplayObjectContainer);
         }
      }

      // =====================================================================================
      //  Volumen
      // =====================================================================================
      private static function clamp(n:Number):Number { return isNaN(n) ? 1 : (n < 0 ? 0 : (n > 1 ? 1 : n)); }

      private static function updateGains():void
      {
         for(var k:String in vols) gains[k] = Number(vols[k]) * Number(vols[k]);
         if(gains["music"] != null) musicGain = gains["music"];
      }

      public static function getVol(id:String):Number
      {
         boot();
         return vols[id] == null ? 1 : Number(vols[id]);
      }

      public static function setVol(id:String, v:Number):void
      {
         vols[id] = clamp(v);
         updateGains();
         if(id == "music") applyMusic();
      }

      /** Sonido de muestra de un grupo (suena al soltar su deslizador). */
      public static function sampleOf(id:String):String
      {
         for each(var g:Object in groups) if(g.id == id) return g.sample;
         return null;
      }

      public static function groupOf(id:String, isMusic:Boolean = false):String
      {
         if(id == null) return isMusic ? "jingles" : "ui";
         var n:String = id;
         if(n.length > 4 && n.substr(n.length - 4) == ".wav") n = n.substr(0, n.length - 4);
         var g:* = soundMap[n];
         if(g != null) return g;
         for each(var p:Array in prefixes) if(n.indexOf(p[0]) == 0) { soundMap[n] = p[1]; return p[1]; }
         return isMusic ? "jingles" : "ui";
      }

      private static function gainOf(group:String):Number
      {
         var g:* = gains[group];
         return g == null ? 1 : Number(g);
      }

      /** Pone la pista de música que suena al volumen actual. */
      public static function applyMusic():void
      {
         try
         {
            var sm:Object = game.soundManager;
            if(sm == null || sm.isMusicMute) return;
            if(sm.fadingWhichTrack != "none") return;
            var ch:SoundChannel = sm.getSoundTrack(sm.playingWhichTrack);
            if(ch != null && sm.playingWhichTrack != "none") ch.soundTransform = new SoundTransform(musicGain);
         }
         catch(e:Error) {}
      }

      /** Parche de SoundManager.playSound: escala la transformación según el grupo del sonido. */
      public static function fx(st:SoundTransform, isMusic:Boolean, id:String):SoundTransform
      {
         if(!booted) boot();
         st.volume = st.volume * gainOf(groupOf(id, isMusic));
         return st;
      }

      /** Parche de SoundManager.playSound: recuerda a qué grupo pertenece el canal que acaba de sonar. */
      public static function reg(ch:*, id:String):*
      {
         if(ch != null) chanGroup[ch] = groupOf(id, false);
         return ch;
      }

      /** Parche de «canal.soundTransform = st» en el juego (sonidos en bucle con volumen propio). */
      public static function setST(a:Array):void
      {
         var o:* = a[0];
         var st:* = a[1];
         if((o is SoundChannel) && (st is SoundTransform))
         {
            var g:* = chanGroup[o];
            o.soundTransform = new SoundTransform(st.volume * gainOf(g == null ? "forge" : g), st.pan);
            return;
         }
         o.soundTransform = st;
      }

      // =====================================================================================
      //  Utilidades / desarrollo
      // =====================================================================================
      public static function log(s:String):void
      {
         trace("[JM] " + s);
         if(dev) devAppend("jm_log.txt", s + "\n");
      }

      private static function devFile(name:String):Object
      {
         return fileClass().applicationStorageDirectory.resolvePath(name);
      }

      private static function devAppend(name:String, s:String):void
      {
         try
         {
            var FS:Class = getDefinitionByName("flash.filesystem.FileStream") as Class;
            var st:Object = new FS();
            st.open(devFile(name), "append");
            st.writeUTFBytes(s);
            st.close();
         }
         catch(e:Error) {}
      }

      /** Laboratorio: órdenes por archivo (jm_cmd.txt en la carpeta de datos de la app). */
      private static function devPoll():void
      {
         try
         {
            var f:Object = devFile("jm_cmd.txt");
            if(!f.exists) return;
            var cmd:String = readText(f).replace(/^\s+|\s+$/g, "");
            f.deleteFile();
            var p:Array = cmd.split(" ");
            if(p[0] == "dump") dump();
            else if(p[0] == "lang") setLang(p[1]);
            else if(p[0] == "tree") tree(p.length > 1 ? p[1] : null);
            else Dev.run(p);
         }
         catch(e:Error) { log("cmd: " + e.message); }
      }

      /** Laboratorio: lista de todos los campos de texto visibles, con su caja y si desbordan. */
      public static function dump():void
      {
         var a:Array = [];
         collect(stage, a);
         var out:String = "";
         for each(var tf:TextField in a)
         {
            if(!vis(tf) || tf.text.length == 0) continue;
            var w:Number = tf.width / Math.abs(tf.scaleX);
            var h:Number = tf.height / Math.abs(tf.scaleY);
            var tx:String = tf.text;
            var lc:Number = tx.charCodeAt(tx.length - 1);
            var tr:int = (lc == 13 || lc == 10) ? 1 : 0;
            var nw:int = tx.replace(/^\s+|\s+$/g, "").split(/\s+/).length;
            var over:Boolean = tf.autoSize == "none" && (tf.textWidth + 4 > w + 1.5 || (tf.maxScrollV > 1 && tf.numLines - tr > 1) || (tf.wordWrap && tf.numLines - tr > nw));
            var o:Object = orig[tf];
            out += (over ? "DESBORDA " : "ok       ") + int(w) + "x" + int(h) + " txt " + int(tf.textWidth) + "x" + int(tf.textHeight) + " tam " + tf.getTextFormat(0, 1).size + (o != null ? "/" + o.size : "") + " " + (tf.wordWrap ? "W" : "-") + (tf.multiline ? "M" : "-") + " " + path(tf) + " :: " + JSON.stringify(tf.text) + "\n";
         }
         var f:Object = devFile("jm_dump.txt");
         var FS:Class = getDefinitionByName("flash.filesystem.FileStream") as Class;
         var st:Object = new FS();
         st.open(f, "write");
         st.writeUTFBytes(out);
         st.close();
      }

      private static function vis(d:DisplayObject):Boolean
      {
         while(d != null) { if(!d.visible) return false; d = d.parent; }
         return true;
      }

      public static function path(d:DisplayObject):String
      {
         var s:String = "";
         var n:int = 0;
         while(d != null && !(d is Stage) && n++ < 7) { s = d.name + (s == "" ? "" : "." + s); d = d.parent; }
         return s;
      }

      /** Laboratorio: árbol de objetos (nombre, clase, posición) bajo un clip cuyo nombre contenga `name`. */
      public static function tree(name:String):void
      {
         var out:Array = [];
         walk(stage, 0, name, name == null, out);
         var FS:Class = getDefinitionByName("flash.filesystem.FileStream") as Class;
         var st:Object = new FS();
         st.open(devFile("jm_tree.txt"), "write");
         st.writeUTFBytes(out.join("\n"));
         st.close();
      }

      private static function walk(c:DisplayObject, depth:int, name:String, on:Boolean, out:Array):void
      {
         var q:String = flash.utils.getQualifiedClassName(c);
         if(!on && ((c.name != null && c.name.indexOf(name) >= 0) || q.indexOf(name) >= 0)) on = true;
         if(on)
         {
            var pad:String = "";
            for(var i:int = 0; i < depth; i++) pad += "  ";
            var extra:String = "";
            if(c is TextField) extra = " TXT " + JSON.stringify((c as TextField).text) + " fmt " + (c as TextField).defaultTextFormat.font + "/" + (c as TextField).defaultTextFormat.size + "/" + Number((c as TextField).defaultTextFormat.color).toString(16) + "/" + (c as TextField).defaultTextFormat.align;
            if(c is flash.display.MovieClip) extra = " frames " + (c as flash.display.MovieClip).totalFrames + " @" + (c as flash.display.MovieClip).currentFrame;
            out.push(pad + c.name + " [" + q + "] x" + c.x.toFixed(1) + " y" + c.y.toFixed(1) + " w" + c.width.toFixed(1) + " h" + c.height.toFixed(1) + " sx" + c.scaleX.toFixed(2) + (c.visible ? "" : " OCULTO") + extra);
         }
         if(c is DisplayObjectContainer && depth < 12)
         {
            var cc:DisplayObjectContainer = c as DisplayObjectContainer;
            for(var j:int = 0; j < cc.numChildren; j++)
            {
               try { walk(cc.getChildAt(j), on ? depth + 1 : depth, name, on, out); } catch(e:Error) {}
            }
         }
      }
   }
}
