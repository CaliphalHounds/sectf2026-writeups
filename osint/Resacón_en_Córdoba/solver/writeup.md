# Resacón en Córdoba

> CTF Track Securiters - RootedCON 2026

> 27/02/2026 18:00 CEST - 01/03/2026 18:00 CEST

* Categoría: OSINT
* Autor: Kesero
* Dificultad: ★★☆
* Etiquetas: OSINT, GEOSINT

## Descripción
    
    Anoche después de descansar, salimos de fiesta. El problema es que la celebración se nos fue de las manos.

    Me he despertado esta mañana famélico, sin recordar absolutamente nada de lo que ocurrió anoche. El piso está patas arriba, tengo cargos extraños en la cuenta y ni Pablo ni David ni Victoria parecen acordarse de nada.

    Por suerte lo único que conservo es una fotografía de una maravillosa mano que tuvo lugar en la timba especial del reencuentro.

    Tenemos que reconstruir la noche para descubrir qué fue lo que sucedió y con quién acabamos.

    Formato de la flag: clctf{lugar,nombre,1ºapellido}.

    Si el lugar es El Corte Inglés y la persona es Pedro Lomana, la flag será clctf{El_Corte_Inglés,Pedro,Lomana}.

    Nota: Este reto tiene distintas partes. Cuando lleguéis al final lo sabréis. Leed con atención la descripción

## Archivos
    
    Timba.jpeg

![](images/Timba.jpeg)

## Resolución

En la esquina inferior izquierda de la imagen proporcionada se encuentra el nombre de usuario de Instagram "pablosanch030".

![](images/1.png)

En el apartado de historias destacadas "Córdoba" se encuentra el primer lugar al que fue el grupo de amigos:

![](images/2.png)

El lugar en cuestión se trata de "Velouria Bar", obtenido mediante una sencilla búsqueda en Google de la imagen:

![](images/3.png)

Buscando el nombre "Velouria Bar" en Google, se obtienen las redes sociales del bar en cuestión:

![](images/4.png)

En su perfil de Instagram, se observan distintos carteles de fiestas pasadas:

![](images/5.png)

Filtrando por el fin de semana en cuestión, se observa que asistieron a la fiesta de carnaval del 21 de febrero.

![](images/6.png)

En dicha publicación se observa un comentario de "david.guutiii", perteneciente a David, uno de sus integrantes.

Además, si se observan las fotos en las que "Velouria Bar" ha sido etiquetado, encontraremos una publicación de David en la que se encuentran vestidos de Spider-Man haciendo la famosa pose señalando.

![](images/7.png)

![](images/8.png)

En el perfil de David se encuentra un apartado en historias destacadas llamado "Córdoba".

![](images/9.png)

![](images/10.png)

En dichas historias, se encuentra el perfil de "victorialo62", perfil perteneciente a Victoria, la última integrante del grupo.

En su perfil se encuentra lo siguiente:

![](images/11.png)

En el perfil de Victoria se encuentra nuevamente un apartado en historias destacadas llamado "Córdoba".

![](images/12.png)

En este caso se encuentra que Victoria ha firmado su puntuación en los dardos con el nombre de usuario "victoriamag2".

Si se busca por dicho usuario en plataformas como Instant Username Search, se observa que dicho usuario está tomado en TikTok y Bluesky:

![](images/13.png)

En la cuenta de Bluesky se observa su perfil de usuario:

![](images/14.png)

En una de sus publicaciones se observa cómo en última instancia, tomaron rumbo a una discoteca:

![](images/15.png)

Buscando en Google por dicho lugar, se llega a la conclusión de que pertenece a la discoteca "Góngora Gran Café".

Además, en su perfil se encuentra la última publicación en la que narran su encuentro con un famoso:

![](images/17.png)

Dicho famoso se trata de Fernando Tejero disfrazado de su personaje emblemático Fermín Trujillo.

> **flag: clctf{Góngora_Gran_Café,Fermín,Trujillo}**