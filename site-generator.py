import yaml
from pathlib import Path
from datetime import datetime

class SiteGenerator:
    def __init__(self, config_path="config.yml"):
        # Load configuration
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Create output directory if it doesn't exist
        Path("output").mkdir(exist_ok=True)

    def generate_nav(self):
        """Generate navigation HTML"""
        nav_items = []
        for item in self.config["nav_items"]:
            nav_items.append('<a href="#{}">'.format(item.lower()) + item + '</a>')
        return "\n".join(nav_items)

    def generate_news(self):
        """Generate news section HTML"""
        news_items = []
        for item in self.config["news"]:
            date_str = item["date"]
            if isinstance(date_str, str):
                # Parse date string into datetime
                date = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date.strftime("%B %d, %Y")
            else:
                formatted_date = date_str.strftime("%B %d, %Y")

            news_items.append("""
                <div class="news-item">
                    <div class="news-date">{}</div>
                    <div class="news-content">
                        {}
                    </div>
                </div>
            """.format(formatted_date, item['content']))
        return "\n".join(news_items)

    def generate_research(self):
        """Generate research section HTML"""
        areas = []
        for area in self.config["research_areas"]:
            areas.append("""
                <div class="research-area">
                    <h3>{}</h3>
                    <p>{}</p>
                </div>
            """.format(area['title'], area['description']))
        return "\n".join(areas)

    def generate_team(self):
        """Generate team section HTML"""
        def process_bio(bio):
            """Properly process multi-line bio"""
            # If bio is a string (which it should be with YAML >), split and clean
            if isinstance(bio, str):
                # Split by newlines, remove any empty lines, strip whitespace
                lines = [line.strip() for line in bio.split('\n') if line.strip()]
                return '<br>'.join(lines)  # Use '<br>' to preserve line breaks
            return bio

        def create_member_section(title, members, is_pi=False):
            """Create HTML for a section of team members"""
            section_html = "<h3>{}</h3>\n".format(title)
            for member in members:
                # Process the bio 
                bio = process_bio(member['bio'])

                if is_pi:
                    section_html += """
                        <div class="team-member">
                            <img src="assets/{}" alt="{}" class="team-member-image">
                            <div class="member-info">
                                <h4>{}</h4>
                                <p class="role">{}</p>
                                <p>{}</p>
                                <p>Email: {}<br>
                                Office: {}</p>
                                <p class="member-links">
                                    {}
                                </p>
                            </div>
                        </div>
                    """.format(
                        member['image'], 
                        member['name'], 
                        member['name'], 
                        member['role'], 
                        bio, 
                        member['email'], 
                        member.get('office', ''),
                        ' | '.join('<a href="{}">{}</a>'.format(link['url'], link['text']) 
                                   for link in member.get('links', []))
                    )
                else:
                    section_html += """
                        <div class="team-member">
                            <img src="assets/{}" alt="{}" class="team-member-image">
                            <div class="member-info">
                                <h4>{}</h4>
                                <p>{}</p>
                                <p>Email: {}</p>
                            </div>
                        </div>
                    """.format(
                        member['image'], 
                        member['name'], 
                        member['name'], 
                        bio, 
                        member['email']
                    )
            return section_html

        # Add Prospective Students section
        prospective_section = """
            <h3>Prospective Students</h3>
            <div class="prospective-content">
                <p>{}</p>
                <p>{}</p>
            </div>
        """.format(
            self.config.get('prospective_students', {}).get('paragraph1', ''),
            self.config.get('prospective_students', {}).get('paragraph2', '')
        )

        # Combine all team sections
        return "\n".join([
            "<h2>Team</h2>",
            create_member_section("Principal Investigator", [self.config["team"]["pi"]], is_pi=True),
            create_member_section("PhD Students", self.config["team"]["phd_students"]),
            create_member_section("MS Students", self.config["team"]["ms_students"]),
            create_member_section("Undergraduate Researchers", self.config["team"]["undergraduates"]),
            prospective_section
        ])

    def generate_site(self):
        """Generate complete website"""
        # Create assets directory if it doesn't exist
        Path("assets").mkdir(exist_ok=True)

        # Read template
        template = Path("template.html").read_text()

        # Replace placeholders
        replacements = {
            "{{lab_name}}": self.config["lab_name"],
            "{{description}}": self.config["description"],
            "{{navigation}}": self.generate_nav(),
            "{{news}}": self.generate_news(),
            "{{research}}": self.generate_research(),
            "{{team}}": self.generate_team(),
            "{{bg_color}}": self.config["style"]["colors"]["bg"],
            "{{text_color}}": self.config["style"]["colors"]["text"],
            "{{accent_color}}": self.config["style"]["colors"]["accent"],
            "{{secondary_color}}": self.config["style"]["colors"]["secondary"],
            "{{header_font}}": self.config["style"]["fonts"]["headers"],
            "{{body_font}}": self.config["style"]["fonts"]["body"],
        }

        html = template
        for placeholder, content in replacements.items():
            html = html.replace(placeholder, content)

        # Write output
        Path("index.html").write_text(html)
        print("Generated site at index.html")

if __name__ == "__main__":
    generator = SiteGenerator()
    generator.generate_site()
