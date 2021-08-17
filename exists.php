<html>
<link rel="stylesheet" id="base" href="/css/default.css" type="text/css" media="screen" />
<title>BsidesSTL vulnerable to blind SQLi</title>
<body>
<h1>Does this blog post exist?</h1>
<p>
<?php
  require("../classes/db.php");
  require("../classes/phpfix.php");
  require("../classes/post.php");

  if (isset($_GET['id'])) {

    $post = Post::find($_GET['id']);

    if (isset($post->id)) {
      echo "This post exists.<br>";
    } else {
      echo "This post does not exist.<br>";
    }

  } else {
    echo "Sorry - please provide a post id (id=1) in the query string";
  }
?>
<?php
  require("footer.php");
?>
</body>
</html>


