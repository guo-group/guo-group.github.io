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

    def generate_header_image(self):
        """Generate header image HTML"""
        return ""               # temporary!!!!!!!!!!
        # Check if a header image is specified in config,
        # or use the first team member's image as a fallback jumpscare
        header_image = self.config.get("header_image")

        if not header_image:
            # Try to get first team member's image
            header_image = self.config.get("team", {}).get("pi", {}).get("image")

        if header_image:
            return f'<img src="assets/{header_image}" alt="Lab Header Image" class="header-image">'

        return ""  # Return empty string if no image found

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
                date = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = f"{date.strftime('%B')} {date.day}, {date.year}"
            else:
                formatted_date = f"{date_str.strftime('%B')} {date_str.day}, {date_str.year}"
            # Generate all photo HTML together in a single container
            photos_html = ""
            if "photos" in item:
                # Start a single photos container
                photos_html = """
                    <div class="news-photos">
                """
                # Add all photos (up to 3) inside the same container
                for photo in item["photos"][:3]:
                    caption = photo.get("caption", "")
                    caption_html = f'<p class="caption">{caption}</p>' if caption else ""
                    photos_html += f"""
                        <div class="news-photo">
                            <img src="assets/{photo['path']}" alt="{caption}">
                            {caption_html}
                        </div>
                    """
                # Close the container
                photos_html += """
                    </div>
                """

            news_items.append(f"""
                <div class="news-item">
                    <div class="news-date">{formatted_date}</div>
                    <div class="news-content">
                        {item.get('content') or ''}
                        {photos_html}
                    </div>
                </div>
            """)

        return "\n".join(news_items)

    def generate_talks(self):
        """Generate upcoming talks section HTML (renders nothing if empty)"""
        talks = self.config.get("talks", [])

        # Normalize dates and keep only upcoming talks
        today = datetime.now().date()
        upcoming = []
        for talk in talks:
            date_str = talk["date"]
            date = datetime.strptime(date_str, "%Y-%m-%d") if isinstance(date_str, str) else date_str
            date = date.date() if isinstance(date, datetime) else date
            if date >= today:
                upcoming.append((date, talk))

        # If nothing upcoming, render nothing at all — no heading, no section
        if not upcoming:
            return ""

        # Soonest first
        upcoming.sort(key=lambda x: x[0])

        items = []
        for date, talk in upcoming:
            formatted_date = f"{date.strftime('%B')} {date.day}, {date.year}"

            # Speaker first, then title in quotes (if present), then venue
            speaker = talk.get("speaker", "")
            venue   = talk.get("venue", "")
            title   = f'"{talk["title"]}"' if talk.get("title") else ""
            parts   = [p for p in [speaker, title, venue] if p]
            content = ", ".join(parts)

            items.append(f"""
                <div class="news-item">
                    <div class="news-date">{formatted_date}</div>
                    <div class="news-content">
                        {content}
                    </div>
                </div>
            """)

        return f"""
            <h2>Upcoming</h2>
            {"".join(items)}
        """

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
            if isinstance(bio, str):
                lines = [line.strip() for line in bio.split('\n') if line.strip()]
                return '<br>'.join(lines)
            return bio

        def create_member_section(title, members, is_pi=False):
            """Create HTML for a section of team members"""
            section_html = "<h3>{}</h3>\n".format(title)
            for member in members:
                bio = process_bio(member['bio'])

                if is_pi:
                    section_html += """
                        <div class="team-member">
                            <img src="assets/{}" alt="{}" class="team-member-image">
                            <div class="member-info">
                                <h4>{}</h4>
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
                                <p>{}</p>
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

        def create_alumni_section(title, alumni):
            """Create HTML for alumni section with simple format"""
            section_html = "<h3>{}</h3>\n".format(title)
            section_html += "<div class=\"alumni-list\">\n"
            for alum in alumni:
                section_html += "<p>{}</p>\n".format(alum['name'])
            section_html += "</div>\n"
            return section_html

        prospective_section = """
            <h3>Prospective Students</h3>
            <div class="prospective-content">
                <p>{}</p>
                <p>{}</p>
                <p>{}</p>
            </div>
        """.format(
            self.config.get('prospective_students', {}).get('paragraph1', ''),
            self.config.get('prospective_students', {}).get('paragraph2', ''),
            self.config.get('prospective_students', {}).get('paragraph3', '')
        )

        return "\n".join([
            "<h2>Team</h2>",
            create_member_section("Principal Investigator", [self.config["team"]["pi"]], is_pi=True),
            create_member_section("PhD Students", self.config["team"]["phd_students"]),
            create_member_section("MS Students", self.config["team"]["ms_students"]),
            create_member_section("Undergraduate Researchers", self.config["team"]["undergraduates"]),
            create_alumni_section("Lab Alumni", self.config["team"]["alums"]),
            prospective_section
        ])

    def generate_publications(self):
        """Generate publications section HTML"""
        scholar_url = self.config.get("scholar_url", "")
        scholar_html = ""
        if scholar_url:
            scholar_html = f"""
                <p class="scholar-note">
                    * denotes equal contribution; † denotes corresponding author
                </p>
            """

        items_html = ""
        for pub in self.config.get("publications", []):
            image_html = ""
            if pub.get("image"):
                image_html = f"""
                    <div class="pub-image">
                        <img src="assets/{pub['image']}" alt="{pub['title']}" loading="lazy">
                    </div>
                """

            # Build the citation line: Venue (Year) Volume:Pages
            citation = f"<em>{pub['venue']}</em> ({pub['year']})"
            if pub.get("volume"):
                citation += f" {pub['volume']}"
            if pub.get("pages"):
                citation += f":{pub['pages']}"

            doi_html = ""
            if pub.get("doi"):
                doi_html = f"""
                    <a class="pub-doi" href="https://doi.org/{pub['doi']}"
                       target="_blank" rel="noopener">DOI: {pub['doi']}</a>
                """

            items_html += f"""
                <div class="pub-item">
                    <div class="pub-number">#{pub['number']}</div>
                    {image_html}
                    <div class="pub-details">
                        <h4 class="pub-title">{pub['title']}</h4>
                        <p class="pub-authors">{pub['authors']}</p>
                        <p class="pub-citation">{citation}</p>
                        {doi_html}
                    </div>
                </div>
            """

        return scholar_html + items_html

    def generate_site(self):
        """Generate complete website"""
        Path("assets").mkdir(exist_ok=True)
        template = Path("template.html").read_text()

        replacements = {
            "{{lab_name}}": self.config.get("lab_name", ""),
            "{{description}}": self.config.get("description", ""),
            "{{header_image}}": self.generate_header_image(),
            "{{navigation}}": self.generate_nav(),
            "{{news}}": self.generate_news(),
            "{{talks}}": self.generate_talks(),
            "{{research}}": self.generate_research(),
            "{{team}}": self.generate_team(),
            "{{publications}}": self.generate_publications(),
            "{{bg_color}}": self.config.get("style", {}).get("colors", {}).get("bg", ""),
            "{{text_color}}": self.config.get("style", {}).get("colors", {}).get("text", ""),
            "{{accent_color}}": self.config.get("style", {}).get("colors", {}).get("accent", ""),
            "{{secondary_color}}": self.config.get("style", {}).get("colors", {}).get("secondary", ""),
            "{{header_font}}": self.config.get("style", {}).get("fonts", {}).get("headers", ""),
            "{{body_font}}": self.config.get("style", {}).get("fonts", {}).get("body", ""),
        }

        html = template
        for placeholder, content in replacements.items():
            html = html.replace(placeholder, str(content))

        Path("index.html").write_text(html)
        print("Generated site at index.html")

if __name__ == "__main__":
    generator = SiteGenerator()
    generator.generate_site()
