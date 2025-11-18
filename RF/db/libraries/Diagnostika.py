# -*- coding: utf-8 -*-

from robot.api import logger
from robot.api.deco import keyword

class Diagnostika:
    """
    Knihovna pro diagnostiku problému s DatabaseLibrary.
    """

    @keyword('Diagnostikuj Databázovou Knihovnu')
    def diagnostikuj_db_knihovnu(self):
        """
        Vypíše všechny atributy načtené DatabaseLibrary a zkontroluje připojení.
        """
        from robot.libraries.BuiltIn import BuiltIn
        try:
            db_lib = BuiltIn().get_library_instance('DatabaseLibrary')
            logger.info("Nalezena instance DatabaseLibrary. Vypisuji její atributy:")
            logger.info("=" * 50)
            # Funkce dir() nám dá seznam všeho, co objekt obsahuje
            atributy = dir(db_lib)
            for attr in atributy:
                logger.info(f"  - {attr}")
            logger.info("=" * 50)

            # Specifická kontrola pro náš problém
            if hasattr(db_lib, '_db_connection'):
                logger.info(f"ATRIBUT '_db_connection' NALEZEN. Jeho hodnota je: {db_lib._db_connection}")
            else:
                logger.error("ATRIBUT '_db_connection' NEBYL NALEZEN. Toto je PŘÍČINA vaší chyby.")
                logger.error("Nejpravděpodobněji máte ve složce s testy soubor 'DatabaseLibrary.py', který překrývá nainstalovanou knihovnu.")

        except Exception as e:
            logger.error(f"Nepodařilo se získat instanci DatabaseLibrary: {e}")
