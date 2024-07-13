import os
import csv
from dataclasses import dataclass, field
from typing import Dict, Set, List

@dataclass
class Contact:
    hq_name: str
    invader: str
    attack: str = ""
    defense: str = ""
    healing: str = ""

@dataclass
class CountryHQ:
    country_code: str
    country_name: str
    aliens: str
    predators: str
    dd_monsters: str

@dataclass
class InvaderInfo:
    country_code: str
    invader_species: str
    role: str
    email: str

@dataclass
class InvaderDatabase:
    country_hq: Dict[str, CountryHQ] = field(default_factory=dict)
    contacts: Dict[str, List[Contact]] = field(default_factory=dict)
    invader_info: List[InvaderInfo] = field(default_factory=list)

    def parse_contacts_from_file(self, file_path: str):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            hq_name = lines[0].split('\t')[0].strip()
            for line in lines[1:]:
                parts = line.strip().split('\t')
                contact = Contact(hq_name, parts[0], 
                                  parts[1] if len(parts) > 1 else '',
                                  parts[2] if len(parts) > 2 else '',
                                  parts[3] if len(parts) > 3 else '')
                if hq_name not in self.contacts:
                    self.contacts[hq_name] = []
                self.contacts[hq_name].append(contact)

    def gather_all_contacts(self, folder_path: str):
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(folder_path, filename)
                self.parse_contacts_from_file(file_path)

    def extract_members_to_dict(self, file_path: str):
        with open(file_path, 'r') as file:
            next(file)  # Skip the header line
            for line in file:
                fields = line.strip().split('\t')
                if len(fields) >= 5:
                    country_hq = CountryHQ(fields[1].strip(), fields[0].strip(), 
                                           fields[2].strip(), fields[3].strip(), fields[4].strip())
                    self.country_hq[country_hq.country_code] = country_hq

    def create_invader_info(self):
        dd_monsters = ['d&d_beholder', 'd&d_devil', 'd&d_lich', 'd&d_mind_flayer', 'd&d_vampire', 
                       'd&d_red_dragon', 'd&d_hill_giant', 'd&d_treant', 'd&d_werewolf', 'd&d_yuan-ti']
        roles = ['attack', 'defense', 'healing']
        
        for country_code, country in self.country_hq.items():
            for role in roles:
                for invader_type in ['aliens', 'predators', 'dd_monsters']:
                    hq_name = getattr(country, invader_type)
                    if hq_name in self.contacts:
                        for contact in self.contacts[hq_name]:
                            if (invader_type == 'dd_monsters' and contact.invader in dd_monsters) or \
                               (invader_type != 'dd_monsters' and contact.invader == invader_type):
                                email = getattr(contact, role)
                                if email:
                                    if not email.endswith('.com'):
                                        email += '@avengers.com'
                                    invader_info = InvaderInfo(country_code, contact.invader, f"{role}_role", email)
                                    self.invader_info.append(invader_info)

        # Correct 'capatain' typo
        for info in self.invader_info:
            info.email = info.email.replace('capatain', 'captain')

    def write_invader_info_to_csv(self, file_path: str):
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Country_Code', 'Invader_Species', 'Role', 'Email']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for info in self.invader_info:
                writer.writerow({
                    'Country_Code': info.country_code,
                    'Invader_Species': info.invader_species,
                    'Role': info.role,
                    'Email': info.email
                })

    def get_unique_emails(self):
        return list(set(info.email for info in self.invader_info))

    def create_email_specific_csv(self, mail: str, output_folder: str):
        os.makedirs(output_folder, exist_ok=True)
        all_hq_names = list(self.contacts.keys())
        all_invaders = list(set(contact.invader for contacts in self.contacts.values() for contact in contacts))

        matrix = {hq: {invader: set() for invader in all_invaders} for hq in all_hq_names}
        mail_prefix = mail.split('@')[0]

        for hq_name, contacts in self.contacts.items():
            for contact in contacts:
                for role in ['attack', 'defense', 'healing']:
                    if getattr(contact, role).split('@')[0] == mail_prefix:
                        matrix[hq_name][contact.invader].add(role[0].upper())

        valid_filename = "".join(c for c in mail_prefix if c.isalnum() or c in (' ', '.', '_')).rstrip()
        output_file_path = os.path.join(output_folder, f"{valid_filename}.csv")

        with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([mail_prefix] + all_invaders)
            for hq in all_hq_names:
                row = [hq] + [''.join(sorted(matrix[hq][invader])) for invader in all_invaders]
                writer.writerow(row)

        print(f"Matrix for email {mail} has been written to {output_file_path}")

def main():
    db = InvaderDatabase()
    country_hq_file_path = "Option2_Tab_Delimited_Text/country_hq.txt"
    contacts_folder_path = "Option2_Tab_Delimited_Text/contacts"

    db.extract_members_to_dict(country_hq_file_path)
    db.gather_all_contacts(contacts_folder_path)
    db.create_invader_info()
    output_file_path = "invader_info_test.csv"
    db.write_invader_info_to_csv(output_file_path)

    print(f"Invader info has been written to {output_file_path}")

    unique_emails = db.get_unique_emails()
    email_matrix_folder = "email_matrices_test"

    for email in unique_emails:
        db.create_email_specific_csv(email, email_matrix_folder)

    print(f"\nEmail-specific matrices have been written to the '{email_matrix_folder}' folder")

if __name__ == "__main__":
    main()