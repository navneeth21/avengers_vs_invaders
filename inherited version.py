from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Invader:
    species: str
    attack: str = ''
    defense: str = ''
    healing: str = ''

    def format_email(self, email):
        email = email.replace('capatain', 'captain')
        if email and not email.lower().endswith('.com'):
            return f"{email}@avengers.com"
        return email

    def create_info(self, country_code: str) -> List['InvaderInfo']:
        info_list = []
        for role in ['attack', 'defense', 'healing']:
            email = getattr(self, role)
            if email:
                formatted_email = self.format_email(email)
                info_list.append(InvaderInfo(country_code, self.species, f"{role}_role", formatted_email))
        return info_list

class Alien(Invader):
    def __init__(self, attack='', defense='', healing=''):
        super().__init__('aliens', attack, defense, healing)

class Predator(Invader):
    def __init__(self, attack='', defense='', healing=''):
        super().__init__('predators', attack, defense, healing)

class DDMonster(Invader):
    def __init__(self, species, attack='', defense='', healing=''):
        super().__init__(species, attack, defense, healing)



class TextDataExtractor:
    @staticmethod
    def extract_members_to_dict(file_path):
        country_hq_dict = {}
        
        with open(file_path, 'r') as file:
            next(file)  # Skip the header line if it exists
            for line in file:
                fields = line.strip().split('\t')
                if len(fields) >= 5:
                    country_name = fields[0].strip()
                    country_hq_dict[country_name] = {
                        'country_code': fields[1].strip(),
                        'aliens': fields[2].strip(),
                        'predators': fields[3].strip(),
                        'dd_monsters': fields[4].strip()
                    }
        
        return country_hq_dict

def gather_all_contacts(folder_path: str) -> Dict[str, List[Contacts]]:
    all_contacts = {}
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            contacts = parse_contacts_from_file(file_path)
            
            # Use the filename (without extension) as the key
            key = os.path.splitext(filename)[0]
            all_contacts[key] = contacts
    
    return all_contacts

def write_invader_info_to_text(file_path: str, invader_info_list: List[InvaderInfo]):
    with open(file_path, 'w') as file:
        # Write header
        file.write("Country_Code\tInvader_Species\tRole\tEmail\n")
        
        # Write data
        for info in invader_info_list:
            file.write(f"{info.country_code}\t{info.invader_species}\t{info.role}\t{info.email}\n")

def write_invader_info_to_csv(file_path: str, invader_info_list: List[InvaderInfo]):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Country_Code', 'Invader_Species', 'Role', 'Email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for info in invader_info_list:
            writer.writerow({
                'Country_Code': info.country_code,
                'Invader_Species': info.invader_species,
                'Role': info.role,
                'Email': info.email
            })

    

if __name__ == "__main__":
    country_hq_file_path = "Option2_Tab_Delimited_Text/country_hq.txt"
    extractor = TextDataExtractor()
    country_hq_dict = extractor.extract_members_to_dict(country_hq_file_path)

    contacts_folder_path = "Option2_Tab_Delimited_Text/contacts"
    all_contacts = gather_all_contacts(contacts_folder_path)

    print(f"\nTotal files processed: {len(all_contacts)}")

    invader_info_list = InvaderInfo.create_invader_info(country_hq_dict, all_contacts)

    # Check if we have 12 invader species for each country
    country_invader_count = {}
    unique_emails = set()

    for info in invader_info_list:
        if info.country_code not in country_invader_count:
            country_invader_count[info.country_code] = set()
        country_invader_count[info.country_code].add(info.invader_species)
        unique_emails.add(info.email)

    for country, invaders in country_invader_count.items():
        if len(invaders) != 12:
            print(f"Warning: Country {country} has {len(invaders)} invader species instead of 12")

    # Print unique email addresses
    print("\nUnique email addresses:")
    for email in sorted(unique_emails):
        print(email)
    print(f"\nTotal unique email addresses: {len(unique_emails)}")

    # Write invader info to CSV
    output_file_path = "invader_info.csv"
    write_invader_info_to_csv(output_file_path, invader_info_list)
    print(f"\nInvader info has been written to {output_file_path}")

    # Get all unique HQ names and invader species
    all_hq_names = set(country_hq_dict.keys())
    all_invader_species = {'aliens', 'predators', 'd&d_beholder', 'd&d_devil', 'd&d_lich', 'd&d_mind_flayer', 
                           'd&d_vampire', 'd&d_red_dragon', 'd&d_hill_giant', 'd&d_treant', 'd&d_werewolf', 'd&d_yuan-ti'}

    # Create and write email-specific matrices
    email_matrix_folder = "email_matrices"
    for email in unique_emails:
        create_email_specific_csv(invader_info_list, email, email_matrix_folder, all_hq_names, all_invader_species)

    print(f"\nEmail-specific matrices have been written to the '{email_matrix_folder}' folder")

    # Write unique emails to a file
    unique_emails_file_path = "unique_emails.txt"
    with open(unique_emails_file_path, 'w') as f:
        for email in sorted(unique_emails):
            f.write(f"{email}\n")
    print(f"Unique email addresses have been written to {unique_emails_file_path}")