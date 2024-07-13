import sqlite3
import os
import csv
from dataclasses import dataclass

# Create or connect to the database
conn = sqlite3.connect('invaders.db')
cursor = conn.cursor()

# Create tables

cursor.execute('''
CREATE TABLE IF NOT EXISTS country_hq (
    country_code TEXT PRIMARY KEY,
    country_name TEXT,
    aliens TEXT,
    predators TEXT,
    dd_monsters TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS contacts (
    hq_name TEXT PRIMARY KEY,
    invader TEXT,
    attack TEXT,
    defense TEXT,
    healing TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS invader_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code TEXT,
    invader_species TEXT,
    role TEXT,
    email TEXT,
    FOREIGN KEY (country_code) REFERENCES country_hq(country_code)
)
''')

conn.commit()

def parse_contacts_from_file(file_path: str):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        hq_name = lines[0].split('\t')[0].strip()
        for line in lines[1:]:
            parts = line.strip().split('\t')
            cursor.execute('''
            INSERT OR REPLACE INTO contacts (hq_name, invader, attack, defense, healing)
            VALUES (?, ?, ?, ?, ?)
            ''', (hq_name, parts[0], parts[1] if len(parts) > 1 else '',
                  parts[2] if len(parts) > 2 else '', parts[3] if len(parts) > 3 else ''))
    conn.commit()

def gather_all_contacts(folder_path: str):
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            parse_contacts_from_file(file_path)

class TextDataExtractor:
    @staticmethod
    def extract_members_to_dict(file_path):
        with open(file_path, 'r') as file:
            next(file)  # Skip the header line
            for line in file:
                fields = line.strip().split('\t')
                if len(fields) >= 5:
                    cursor.execute('''
                    INSERT OR REPLACE INTO country_hq (country_code, country_name, aliens, predators, dd_monsters)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (fields[1].strip(), fields[0].strip(), fields[2].strip(),
                          fields[3].strip(), fields[4].strip()))
        conn.commit()

def create_invader_info():
    dd_monsters = ['d&d_beholder', 'd&d_devil', 'd&d_lich', 'd&d_mind_flayer', 'd&d_vampire', 
                   'd&d_red_dragon', 'd&d_hill_giant', 'd&d_treant', 'd&d_werewolf', 'd&d_yuan-ti']
    
    roles = ['attack', 'defense', 'healing']
    
    for role in roles:
        cursor.execute(f'''
        INSERT INTO invader_info (country_code, invader_species, role, email)
        SELECT 
            chq.country_code,
            CASE 
                WHEN c.invader IN ('aliens', 'predators') THEN c.invader
                ELSE c.invader
            END AS invader_species,
            '{role}_role' AS role,
            CASE 
                WHEN c.{role} LIKE '%.com' THEN c.{role}
                WHEN c.{role} IS NOT NULL AND c.{role} != '' THEN c.{role} || '@avengers.com'
                ELSE NULL
            END AS email
        FROM country_hq chq
        JOIN contacts c ON 
            (chq.aliens = c.hq_name AND c.invader = 'aliens') OR
            (chq.predators = c.hq_name AND c.invader = 'predators') OR
            (chq.dd_monsters = c.hq_name AND c.invader IN ({','.join(['?']*len(dd_monsters))}))
        WHERE c.{role} IS NOT NULL AND c.{role} != ''
        ''', dd_monsters)

    conn.commit()

    # Correct 'capatain' typo
    cursor.execute('''
    UPDATE invader_info
    SET email = REPLACE(email, 'capatain', 'captain')
    ''')
    conn.commit()

    
def get_unique_emails():
    cursor.execute('SELECT DISTINCT email FROM invader_info')
    return [row[0] for row in cursor.fetchall()]


def create_email_specific_csv(mail, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    #print('email received is ', mail)
    # Get unique HQ names and country codes
    '''
    cursor.execute('SELECT country_code, country_name FROM country_hq')
    country_to_hq = {row[0]: row[1] for row in cursor.fetchall()}
    all_hq_names = list(country_to_hq.values())
    '''
    cursor.execute('SELECT DISTINCT hq_name FROM contacts')
    all_hq_names = [row[0] for row in cursor.fetchall()]

    # Get unique invaders from contacts table
    cursor.execute('SELECT DISTINCT invader FROM contacts')
    all_invaders = [row[0] for row in cursor.fetchall()]

    # Create the matrix
    matrix = {hq: {invader: set() for invader in all_invaders} for hq in all_hq_names}
    mail = mail.split('@')[0]  # Get the portion before @
    # Fill the matrix
    cursor.execute('''
        SELECT hq_name, attack, defense, healing, invader
        FROM contacts 
        WHERE attack = ? OR defense = ? OR healing = ?
    ''', (mail, mail, mail))

    
    

    for hq, att, defe, heal, inv in cursor.fetchall():
        att=att.split('@')[0]
        defe=defe.split('@')[0]
        heal = heal.split('@')[0]
        #print(inv,'inv', att,'attack ', defe, 'defense', heal,'heal','saviour is ', mail)
        if hq in matrix and inv in matrix[hq]:
            
            #print(att, mail)
            if att == mail:
                
                matrix[hq][inv].add('A')
            if defe == mail:
                matrix[hq][inv].add('D')
            if heal == mail:
                matrix[hq][inv].add('H')

        #print(hq,'hqs','attack ', att, defe, heal,'saviour is ', mail)
    # Create the CSV file
    valid_filename = "".join(c for c in mail if c.isalnum() or c in (' ', '.', '_')).rstrip()
    output_file_path = os.path.join(output_folder, f"{valid_filename}.csv")
    
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow([mail] + all_invaders)
        
        # Write data
        for hq in all_hq_names:
            row = [hq] + [''.join(sorted(matrix[hq][invader])) for invader in all_invaders]
            writer.writerow(row)
    
    print(f"Matrix for email {mail} has been written to {output_file_path}")
    
if __name__ == "__main__":
    try:
        country_hq_file_path = "Option2_Tab_Delimited_Text/country_hq.txt"
        contacts_folder_path = "Option2_Tab_Delimited_Text/contacts"

        TextDataExtractor.extract_members_to_dict(country_hq_file_path)
        gather_all_contacts(contacts_folder_path)

        create_invader_info()
        cursor.execute('SELECT DISTINCT email FROM invader_info')
        unique_emails = [row[0] for row in cursor.fetchall()]

        # Create and write email-specific matrices
        email_matrix_folder = "email_matrices"
        for email in unique_emails:
           # print('email being passed is',email)
            create_email_specific_csv(email, email_matrix_folder)

        #print(f"\nEmail-specific matrices have been written to the '{email_matrix_folder}' folder")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()