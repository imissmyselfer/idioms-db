import sqlite3

def update_tags(idiom_list, tag_value):
    conn = sqlite3.connect('idioms-db/idioms.db')
    cursor = conn.cursor()
    
    updated_count = 0
    for idiom_name in idiom_list:
        cursor.execute('UPDATE idioms SET tag = ? WHERE name = ?', (tag_value, idiom_name))
        if cursor.rowcount > 0:
            updated_count += 1
        else:
            print(f"找不到成語: {idiom_name}")
            
    conn.commit()
    conn.close()
    print(f"已成功標註 {updated_count} 個成語為 '{tag_value}'。")

if __name__ == "__main__":
    # 在這裡填入你的第一批 50 個成語
    first_batch = [
        "八面玲瓏", "百發百中", "半途而廢", # ... 範例
    ]
    
    if first_batch:
        update_tags(first_batch, "常用-1")
