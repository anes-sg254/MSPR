from config_db import connect_to_db

# Fonction pour établir une connexion à la base de données
def connect_to_database():
    return connect_to_db()

# Fonction pour créer la table NewCases
def create_NewCases_table(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS NewCases (
                    "NewCasesID" SERIAL PRIMARY KEY,
                    "CountryID" INT NOT NULL,
                    "RegionID" INT,
                    "Date" DATE NOT NULL,
                    "NewCases" INT NOT NULL,
                    FOREIGN KEY ("CountryID") REFERENCES Pays("id") ON DELETE SET NULL,
                    FOREIGN KEY ("RegionID") REFERENCES Region("RegionID") ON DELETE SET NULL
                );
            """)
            conn.commit()
            print("Table NewCases vérifiée/créée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création ou vérification de la table NewCases : {e}")


# Fonction principale pour exécuter le processus complet
def main():
    # Connexion à la base de données
    conn = connect_to_database()

    # Créer la table NewCases
    create_NewCases_table(conn)

    # Fermer la connexion
    conn.close()
    print("Connexion à la base de données fermée.")

if __name__ == "__main__":
    main()
