def apply_cloud_style(app):
    style = app.style
    style.configure('TFrame', background='#f0f0f0')
    style.configure('TLabel', background='#f0f0f0', font=('Arial', 12))
    style.configure('TEntry', font=('Arial', 12))
    style.configure('TButton', background='#0078d7', foreground='white', font=('Arial', 12, 'bold'), padding=10)
    style.configure('TProgressbar', troughcolor='#f0f0f0', background='#0078d7')
    style.map('TButton', background=[('active', '#0053a0')])
