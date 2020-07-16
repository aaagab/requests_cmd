#!/usr/bin/env python3

if __name__ == "__main__":
    import sys, os
    import importlib
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    pkg.ft.clear_screen()
    pkg.ft.clear_scrolling_history()

    print(pkg.ft.error("error message"))
    print(pkg.ft.info("info message"))
    print(pkg.ft.success("success message"))
    print(pkg.ft.warning("warning message"))

    print()

    print(pkg.ft.log(indent="  ", bullet="error", text="error message as a known label"))
    print(pkg.ft.log(indent="  ", bullet="info", text="info message as a known label"))
    print(pkg.ft.log(indent="  ", bullet="success", text="success message as a known label"))
    print(pkg.ft.log(indent="  ", bullet="warning", text="warning message as a known label"))

    print()
    for bullet in sorted(pkg.ft.get_bullets()):
        print(pkg.ft.log(bullet=bullet, indent="\t\t"))

    print()
    for bullet in ["error", "info", "success", "warning"]:
        print(pkg.ft.log(bullet=bullet, text="log format as a known label"))

    txt="color as a function"
    print(pkg.ft.black(txt))
    print(pkg.ft.red(txt))
    print(pkg.ft.green(txt))
    print(pkg.ft.brown(txt))
    print(pkg.ft.blue(txt))
    print(pkg.ft.magenta(txt))
    print(pkg.ft.cyan(txt))
    print(pkg.ft.lgray(txt))
    print(pkg.ft.dgray(txt))
    print(pkg.ft.lred(txt))
    print(pkg.ft.lgreen(txt))
    print(pkg.ft.yellow(txt))
    print(pkg.ft.lblue(txt))
    print(pkg.ft.lmagenta(txt))
    print(pkg.ft.lcyan(txt))
    print(pkg.ft.white(txt))
    txt="emphasize as a function"
    print(pkg.ft.uline(txt))
    print(pkg.ft.bold(txt))
    print(pkg.ft.iverse(txt))

    print()

    for color_name in sorted(pkg.ft.get_colors()):
        print(pkg.ft.color(color_name, color_name))

    for mark_name in sorted(pkg.ft.get_marks()):
        print(pkg.ft.mark(mark_name, mark_name))


    print()
    print(pkg.ft.wrap(
        "This is a long <bold>wrapped</bold> text, <yellow>that is going to be wrapped according to the size</yellow> of the terminal or the the user chosen size, you can also provide an indent so the wrapped size is set according to the indent size. There is a minimum line width (width-indent) = 1 and no maximum width'", 
        indent="\t\t",
        style=True,
        width="auto"
    ))

    print()
    print(pkg.ft.wrap(
        "This is a long <bold>wrapped</bold> text, <yellow>that is going to be wrapped according to the size</yellow> of the terminal or the the user chosen size, <iverse>you can also provide an indent</iverse> so the wrapped size is set according to the indent <lgreen>size</lgreen>. There is a minimum line width (width-indent) = 1 and no <uline>maximum width</uline>'", 
        indent="\t\t",
        style=True,
    ))


    print()
    print(pkg.ft.wrap(
        "This is a long wrapped text, that is going to be wrapped according to the size of the terminal or the the user chosen size, you can also provide an indent so the wrapped size is set according to the indent size. There is a minimum line width (width-indent) = 1 and no maximum width'", 
        indent="\t\t"
    ))

    print()
    print(pkg.ft.wrap(
        "This is a long wrapped text, that is going to be wrapped according to the size of the terminal or the the user chosen size, you can also provide an indent so the wrapped size is set according to the indent size. There is a minimum line width (width-indent) = 1 and no maximum width'", 
        indent="\t\t\t",
        width=30,
    ))

    print()
    print(pkg.ft.wrap(
        "This is a long wrapped text, that is going to be wrapped according to the size of the terminal or the the user chosen size, you can also provide an indent so the wrapped size is set according to the indent size. There is a minimum line width (width-indent) = 1 and no maximum width'", 
        width=None,
    ))

    print()
    print(pkg.ft.log(
        "This is a long wrapped text, that is going to be wrapped according to the size of the terminal or the the user chosen size, you can also provide an indent so the wrapped size is set according to the indent size. There is a minimum line width (width-indent) = 1 and no maximum width'", 
        indent="\t",
        bullet="success",
        width=40,
    ))


    print()
    print(pkg.ft.log(
        text="bullet test", 
        indent="\t",
        bullet="+",
        width=40,
    ))

    print()
    print(pkg.ft.log(
        text="bullet test", 
        indent="\t",
        bullet="<lmagenta>-></lmagenta>",
        width=40,
    ))

    print()
    print(pkg.ft.log(
        text="", 
        indent="\t",
        bullet="<lmagenta>-></lmagenta>",
        width=40,
    ))


    print()
    text="<green>that is <red>my</red>, text <uline>with multiple</uline> formatting</green>."
    print("original text: '{}'".format(text))
    print(pkg.ft.log(text=text, style=True))
    print(pkg.ft.log(text=text+" and format disabled.", style=True, format=False))

    print()
    print(pkg.ft.info("Showing nesting style, works for words only not letters"))
    text="<red>This is nested styled ,<cyan><uline>other '<green>VAR_NAME</green>' middle</uline> text</cyan></red>."
    print("original text: '{}'".format(text))
    print(pkg.ft.log(text,style=True))
    print(pkg.ft.log(text,style=True, format=False))
