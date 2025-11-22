"""Command-line interface for XOR file encryption."""

import argparse
import getpass
from encryption import encrypt_file, decrypt_file

def main():
    parser = argparse.ArgumentParser(
        description='XOR-based File Encryption Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py encrypt myfile.txt
  python cli.py decrypt myfile.txt.encrypted -o myfile.txt
  python cli.py encrypt document.pdf -o document.pdf.enc -p mypassword
        """
    )
    
    parser.add_argument(
        'action',
        choices=['encrypt', 'decrypt'],
        help='Action to perform'
    )
    
    parser.add_argument(
        'input_file',
        help='Input file path'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: input_file.encrypted or input_file.decrypted)'
    )
    
    parser.add_argument(
        '-p', '--password',
        help='Password (if not provided, you will be prompted)'
    )
    
    args = parser.parse_args()
    
    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Enter password: ")
        confirm = getpass.getpass("Confirm password: ")
        
        if password != confirm:
            print("✗ Passwords do not match!")
            return
    
    if args.output:
        output_file = args.output
    else:
        if args.action == 'encrypt':
            output_file = f"{args.input_file}.encrypted"
        else:
            output_file = f"{args.input_file}.decrypted"
    
    if args.action == 'encrypt':
        encrypt_file(args.input_file, output_file, password)
    else:
        decrypt_file(args.input_file, output_file, password)

if __name__ == '__main__':
    main()
