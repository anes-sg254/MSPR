from config_db import connect_to_db

# Fonction pour établir une connexion à la base de données
def connect_to_database():
    return connect_to_db()

# Fonction pour créer la table Region
def create_region_table(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Region (
                    "RegionID" SERIAL PRIMARY KEY,
                    "Region" VARCHAR(100) NOT NULL
                );
            """)
            conn.commit()
            print("Table Region vérifiée/créée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création ou vérification de la table Region : {e}")

# Fonction principale pour exécuter le processus complet
def main():
    # Connexion à la base de données
    conn = connect_to_database()

    # Créer la table Region
    create_region_table(conn)

    # Fermer la connexion
    conn.close()
    print("Connexion à la base de données fermée.")

if __name__ == "__main__":
    main()
