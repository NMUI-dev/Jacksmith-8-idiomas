package
{
   import flash.display.Sprite;
   import jm.JM;
   import jm.Dev;
   import jm.Options;
   import jm.LangPick;

   /** Clase raíz solo para que el compilador incluya el núcleo; su código (ABC) se inyecta en Main.assets. */
   public class JMCore extends Sprite
   {
      public function JMCore()
      {
         super();
         var a:Array = [JM, Dev, Options, LangPick];
      }
   }
}
