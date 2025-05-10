import sys
import os
import tempfile
import requests
import weasyprint
import trafilatura
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def extract_reader_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                main_content = trafilatura.extract(downloaded, include_comments=False, include_tables=False, output_format="html")
                return main_content or ''
            else:
                print(Fore.YELLOW + f'Could not extract main content for {url}. This site may use paywalls, require login, or block automated tools.' + Style.RESET_ALL)
                return ''
        elif response.status_code == 403:
            print(Fore.YELLOW + f'Access denied (HTTP 403) for {url}. This site may block bots or require login/subscription.' + Style.RESET_ALL)
            return ''
        elif response.status_code == 404:
            print(Fore.YELLOW + f'Page not found (HTTP 404) for {url}.' + Style.RESET_ALL)
            return ''
        else:
            print(Fore.YELLOW + f'Failed to fetch {url}: HTTP {response.status_code}. The site may block bots, require login, or be unavailable.' + Style.RESET_ALL)
            return ''
    except Exception as e:
        print(Fore.RED + f'Error extracting from {url}: {e}\nThis may be due to network issues, site restrictions, or unsupported content.' + Style.RESET_ALL)
        return ''

def print_heading():
    heading = r'''
  _   _ _____ __  __ _   _____ ___  ____  ____  _____ 
| | | |_   _|  \/  | | |_   _/ _ \|  _ \|  _ \|  ___|
| |_| | | | | |\/| | |   | || | | | |_) | | | | |_   
|  _  | | | | |  | | |___| || |_| |  __/| |_| |  _|  
|_| |_| |_| |_|  |_|_____|_| \___/|_|   |____/|_|    
 
'''
    print(Fore.GREEN + heading + Style.RESET_ALL)
    print(Fore.GREEN + 'Welcome to HTML TO PDF' + Style.RESET_ALL)
    print(Fore.GREEN + '-'*60 + Style.RESET_ALL)

def interactive_menu():
    print_heading()
    print(Fore.GREEN + 'Options:' + Style.RESET_ALL)
    print(Fore.GREEN + '1. Convert a single URL to PDF' + Style.RESET_ALL)
    print(Fore.GREEN + '2. Convert a .txt file of URLs to a combined PDF' + Style.RESET_ALL)
    print(Fore.GREEN + 'Q. Quit' + Style.RESET_ALL)
    choice = input(Fore.GREEN + 'Enter your choice (1/2/Q): ' + Style.RESET_ALL).strip().lower()
    return choice

def convert_single_url():
    url = input(Fore.GREEN + 'Enter the URL to convert: ' + Style.RESET_ALL).strip()
    if not url:
        print(Fore.GREEN + 'No URL entered. Returning to menu.' + Style.RESET_ALL)
        return
    print(Fore.GREEN + f'Processing {url}...' + Style.RESET_ALL)
    html = extract_reader_text(url)
    if not html:
        print(Fore.GREEN + 'Failed to extract content from the URL.' + Style.RESET_ALL)
        return
    section = f'<div class="site-section">'
    section += f'<h2>Website</h2>'
    section += f'<a class="site-link" href="{url}">{url}</a>'
    section += f'<div>{html}</div>'
    section += '</div>'
    # PDF HTML: neutral style (no green/black)
    full_html = '''<!DOCTYPE html>\n<html>\n<head>\n  <meta charset="utf-8">\n  <style>body { font-family: Arial, sans-serif; margin: 2em; color: #222; background: #fff; } h1 { color: #2a4d7a; } h2 { color: #2a4d7a; margin-bottom: 0.2em; } a { color: #1a0dab; text-decoration: underline; } .site-section { margin-bottom: 60px; } .site-link { font-size: 0.95em; margin-bottom: 1em; display: block; } .page-break { page-break-before: always; } hr { border: none; border-top: 1px solid #ccc; margin: 2em 0; }</style>\n</head>\n<body>\n  <h1>Website Story</h1>\n'''
    full_html += section
    full_html += '\n</body>\n</html>'
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
        tmp.write(full_html.encode('utf-8'))
        tmp_path = tmp.name
    output_pdf = 'output_single.pdf'
    weasyprint.HTML(tmp_path).write_pdf(output_pdf)
    print(Fore.GREEN + f'PDF generated: {output_pdf}' + Style.RESET_ALL)
    os.remove(tmp_path)

def main():
    while True:
        choice = interactive_menu()
        if choice == '1':
            convert_single_url()
        elif choice == '2':
            txt_file = input(Fore.GREEN + 'Enter the path to the .txt file: ' + Style.RESET_ALL).strip()
            if not os.path.isfile(txt_file):
                print(Fore.GREEN + f'File not found: {txt_file}' + Style.RESET_ALL)
                continue
            with open(txt_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            temp_files = []
            sections = []
            for idx, url in enumerate(urls):
                print(Fore.GREEN + f'Processing {url}...' + Style.RESET_ALL)
                try:
                    html = extract_reader_text(url)
                    if html:
                        section = ''
                        if idx > 0:
                            section += '<div class="page-break"></div>'
                        section += f'<div class="site-section">'
                        section += f'<h2>Website {idx+1}</h2>'
                        section += f'<a class="site-link" href="{url}">{url}</a>'
                        section += f'<div>{html}</div>'
                        section += '</div>'
                        sections.append(section)
                except Exception as e:
                    print(Fore.GREEN + f'Failed to process {url}: {e}' + Style.RESET_ALL)
            # PDF HTML: neutral style (no green/black)
            full_html = '''<!DOCTYPE html>\n<html>\n<head>\n  <meta charset="utf-8">\n  <style>body { font-family: Arial, sans-serif; margin: 2em; color: #222; background: #fff; } h1 { color: #2a4d7a; } h2 { color: #2a4d7a; margin-bottom: 0.2em; } a { color: #1a0dab; text-decoration: underline; } .site-section { margin-bottom: 60px; } .site-link { font-size: 0.95em; margin-bottom: 1em; display: block; } .page-break { page-break-before: always; } hr { border: none; border-top: 1px solid #ccc; margin: 2em 0; }</style>\n</head>\n<body>\n  <h1>Combined Website Stories</h1>\n'''
            full_html += '\n'.join(sections)
            full_html += '\n</body>\n</html>'
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
                tmp.write(full_html.encode('utf-8'))
                tmp_path = tmp.name
                temp_files.append(tmp_path)
            output_pdf = 'output.pdf'
            weasyprint.HTML(tmp_path).write_pdf(output_pdf)
            print(Fore.GREEN + f'PDF generated: {output_pdf}' + Style.RESET_ALL)
            for f in temp_files:
                try:
                    os.remove(f)
                except Exception as e:
                    print(Fore.GREEN + f'Could not delete temp file {f}: {e}' + Style.RESET_ALL)
        elif choice == 'q':
            print(Fore.GREEN + 'Goodbye!' + Style.RESET_ALL)
            break
        else:
            print(Fore.GREEN + 'Invalid choice. Please try again.' + Style.RESET_ALL)

if __name__ == '__main__':
    main()