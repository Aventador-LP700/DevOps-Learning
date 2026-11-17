def fixtures(work):
    public, private = work / "public", work / "private"
    public.mkdir(exist_ok=True); private.mkdir(exist_ok=True)
    (public / "welcome.txt").write_text("Synthetic public welcome")
    (private / "payroll.txt").write_text("SYNTHETIC_PRIVATE_PAYROLL")
    return public
