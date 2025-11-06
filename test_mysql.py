#!/usr/bin/env python3
"""
MySQL Connection Test Script
"""

import pymysql
import os

def test_mysql_connection():
    """Test MySQL connection with different configurations"""
    
    # Configuration options to try
    configs = [
        {
            'host': 'localhost',
            'port': 8889,
            'user': 'root',
            'password': 'root',
            'name': 'MAMP/Local MySQL (port 8889)'
        },
        {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'root',
            'name': 'Standard MySQL (port 3306)'
        },
        {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'name': 'MySQL with empty password'
        },
        {
            'host': '127.0.0.1',
            'port': 8889,
            'user': 'root',
            'password': 'root',
            'name': 'MAMP with 127.0.0.1'
        }
    ]
    
    print("Testing MySQL connections...")
    print("=" * 50)
    
    for config in configs:
        try:
            print(f"\nTrying: {config['name']}")
            print(f"Host: {config['host']}:{config['port']}")
            print(f"User: {config['user']}")
            
            connection = pymysql.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                charset='utf8mb4'
            )
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"✅ SUCCESS! MySQL Version: {version[0]}")
                
                # List databases
                cursor.execute("SHOW DATABASES")
                databases = cursor.fetchall()
                print(f"Available databases: {[db[0] for db in databases]}")
                
                # Check if our database exists
                cursor.execute("SHOW DATABASES LIKE 'alysa-db'")
                db_exists = cursor.fetchone()
                if db_exists:
                    print("✅ Database 'alysa-db' already exists")
                else:
                    print("ℹ️  Database 'alysa-db' does not exist (will be created)")
            
            connection.close()
            
            # Return successful config
            return {
                'host': config['host'],
                'port': config['port'],
                'user': config['user'],
                'password': config['password']
            }
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 50)
    print("❌ Could not connect to MySQL with any configuration!")
    print("\nTroubleshooting steps:")
    print("1. Make sure MySQL server is running")
    print("2. If using MAMP: Start MAMP and check the ports in preferences")
    print("3. If using Homebrew MySQL: brew services start mysql")
    print("4. Check your MySQL credentials")
    
    return None

def create_database_with_config(config):
    """Create database with successful config"""
    try:
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS `alysa-db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ Database 'alysa-db' created successfully!")
        
        connection.commit()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == "__main__":
    config = test_mysql_connection()
    
    if config:
        print(f"\n🎉 Found working MySQL configuration!")
        print(f"Connection string: mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/alysa-db")
        
        # Try to create the database
        create_database_with_config(config)
        
        print(f"\nUpdate your .env file with:")
        print(f"DB_HOST={config['host']}")
        print(f"DB_PORT={config['port']}")
        print(f"DB_USER={config['user']}")
        print(f"DB_PASSWORD={config['password']}")
        print(f"DB_NAME=alysa-db")
    else:
        print("\n❌ Please fix MySQL connection issues before proceeding.")
