"""
Database Browser - Tool untuk lihat isi database
"""

import sqlite3
import os
from tabulate import tabulate

def browse_database(db_path='payroll.db'):
    """Browse database dan tampilkan isi semua table"""
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database tidak ditemukan: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("="*80)
    print("DATABASE BROWSER - MPI Payroll System")
    print("="*80)
    print(f"Database: {db_path}\n")
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    if not tables:
        print("[!] Database kosong, belum ada table")
        conn.close()
        return
    
    print(f"[OK] Ditemukan {len(tables)} tables\n")
    
    # Browse each table
    for table in tables:
        table_name = table[0]
        
        # Get count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        print("-"*80)
        print(f"TABLE: {table_name.upper()} ({count} records)")
        print("-"*80)
        
        if count == 0:
            print("[!] Table kosong\n")
            continue
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get all data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Print as table
        if rows:
            # Format data untuk display
            formatted_rows = []
            for row in rows:
                formatted_row = []
                for item in row:
                    if isinstance(item, float):
                        formatted_row.append(f"{item:,.0f}")
                    elif isinstance(item, str) and len(item) > 50:
                        formatted_row.append(item[:47] + "...")
                    else:
                        formatted_row.append(str(item))
                formatted_rows.append(formatted_row)
            
            try:
                print(tabulate(formatted_rows, headers=columns, tablefmt='grid'))
            except:
                # Fallback jika tabulate tidak tersedia
                print(f"Columns: {', '.join(columns)}")
                for i, row in enumerate(rows, 1):
                    print(f"[{i}] {row}")
        
        print()
    
    conn.close()
    print("="*80)
    print("[DONE] Database browsing selesai")
    print("="*80)


if __name__ == '__main__':
    import sys
    
    # Get database path from argument or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'payroll.db'
    
    browse_database(db_path)
