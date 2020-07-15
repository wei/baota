<?php
function adminer_object() {
    include_once "./plugins/plugin.php";
    

    foreach (glob("plugins/*.php") as $filename) {
        include_once "./$filename";
    }
    
    $plugins = array(
       new AdminerDatabaseHide(array('information_schema')),
		new AdminerDumpJson,
		new AdminerDumpBz2,
		new AdminerDumpZip,
		new AdminerDumpXml,
		new AdminerDumpAlter,
		new AdminerFileUpload("/"),
		new AdminerJsonColumn,
		new AdminerSlugify,
		new AdminerTranslation,
		new AdminerForeignSystem,
		new AdminerEnumOption,
		new AdminerTablesFilter,
		new AdminerEditForeign,
    );
    

    return new AdminerPlugin($plugins);
}
include "./adminer.php";
?>