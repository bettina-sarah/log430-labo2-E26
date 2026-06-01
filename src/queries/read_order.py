"""
Orders (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from db import get_sqlalchemy_session, get_redis_conn
from sqlalchemy import desc
from models.order import Order
from collections import defaultdict

def get_order_by_id(order_id):
    """Get order by ID from Redis"""
    r = get_redis_conn()
    return r.hgetall(order_id)

def get_orders_from_mysql(limit=9999):
    """Get last X orders"""
    session = get_sqlalchemy_session()
    return session.query(Order).order_by(desc(Order.id)).limit(limit).all()

def get_orders_from_redis(limit=9999):
    """Get last X orders from Redis cleanly"""
    r = get_redis_conn()
    orders = []
    
    class RedisOrder:
        def __init__(self, order_id, total_amount):
            self.id = order_id
            self.total_amount = total_amount

    try:
        order_keys = r.keys("order:*")
        
        for key in order_keys:
            order_data = r.hgetall(key)

            if order_data and (b'total' in order_data or 'total' in order_data):
                try:
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                    order_id = int(key_str.split(":")[-1])
                    
                    total_val = order_data.get(b'total') or order_data.get('total')
                    
                    total_amount = float(total_val.decode('utf-8') if isinstance(total_val, bytes) else total_val)
                    
                    orders.append(RedisOrder(order_id, total_amount))
                except Exception as parse_err:
                    print(f"[Redis] Erreur de parsing pour la clé {key}: {parse_err}")
                    continue
                    
        orders.sort(key=lambda x: x.id, reverse=True)
        return orders[:limit]

    except Exception as e:
        print(f"[Redis] Erreur critique lors de la lecture : {e}")
        return [] 

def get_highest_spending_users():
    """Get report of highest spending users"""
    r = get_redis_conn()
    expenses_by_user = defaultdict(float)

    try:
        order_keys = r.keys("order:*")
        print(f"-> [Debug] Clés trouvées pour le rapport : {len(order_keys)}", flush=True)

        for key in order_keys:
            order_data = r.hgetall(key)
            
            total_key = b'total' if b'total' in order_data else 'total'
            user_key = b'user_id' if b'user_id' in order_data else 'user_id'
            
            if order_data and total_key in order_data and user_key in order_data:
                try:
                    val_user = order_data[user_key]
                    val_total = order_data[total_key]
                    
                    user_str = val_user.decode('utf-8') if isinstance(val_user, bytes) else str(val_user)
                    total_str = val_total.decode('utf-8') if isinstance(val_total, bytes) else str(val_total)
                    
                    if user_str == 'None' or user_str.strip() == '':
                        continue 
                    
                    user_id = int(float(user_str))
                    total = float(total_str)
                    
                    expenses_by_user[user_id] += total
                except Exception as parse_err:
                    print(f"-> [Debug] Erreur de parsing pour {key}. Valeurs: user={val_user}, total={val_total}. Erreur: {parse_err}"
                          , flush=True)
                    continue
            
        print(f"-> [Debug] Dépenses brutes par utilisateur : {dict(expenses_by_user)}", flush=True)
        
        highest_spending_users = sorted(expenses_by_user.items(), key=lambda item: item[1], reverse=True)
        return highest_spending_users[:10]

    except Exception as e:
        print(f"[Redis] Erreur critique lors du rapport : {e}", flush=True)
        return []

def get_best_sellers():
    """Récupère et trie les produits par quantité vendue depuis Redis"""
    r = get_redis_conn()
    top_products = r.zrevrange("top_products", 0, 9, withscores=True)
    
    return [{"product_id": pid.decode('utf-8'), "total_sold": int(qty)} 
            for pid, qty in top_products]