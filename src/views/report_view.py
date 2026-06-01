"""
Report view
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from views.template_view import get_template, get_param
from controllers.order_controller import get_report_highest_spending_users, get_report_best_sellers

def show_highest_spending_users():
    """ Show report of highest spending users """
    top_buyers = get_report_highest_spending_users()
    
    row_patterns = []
    for user_id, total_spent in top_buyers:
        row_patterns.append(f"""
            <tr>
                <td>Utilisateur #{user_id}</td>
                <td>${total_spent:.2f}</td>
            </tr>
        """)
        
    return get_template(f"""
        <h2>Les plus gros acheteurs</h2>
        <p>Voici les 10 utilisateurs ayant dépensé le plus sur la plateforme :</p>
        <table class="table">
            <thead>
                <tr>
                    <th>Utilisateur</th>
                    <th>Total Dépensé</th>
                </tr>
            </thead>
            <tbody>
                {" ".join(row_patterns) if row_patterns else "<tr><td colspan='2'>Aucune donnée disponible</td></tr>"}
            </tbody>
        </table>
        <br>
        <a href="/orders">← Retourner à la page des commandes</a>
    """)

def show_best_sellers():
    """ Show report of best selling products """
    best_sellers = get_report_best_sellers()
    
    row_patterns = []
    for p in best_sellers:
        row_patterns.append(f"""
            <tr>
                <td>Article #{p['product_id']}</td>
                <td>{p['total_sold']} unités vendues</td>
            </tr>
        """)
        
    return get_template(f"""
        <h2>Les articles les plus vendus</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>Article</th>
                    <th>Total Vendu</th>
                </tr>
            </thead>
            <tbody>
                {" ".join(row_patterns) if row_patterns else "<tr><td colspan='2'>Aucune donnée disponible</td></tr>"}
            </tbody>
        </table>
        <br>
        <a href="/orders">← Retourner à la page des commandes</a>
    """)