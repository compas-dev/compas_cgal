from compas_cgal._cgal import hello


def main():
    hello.hello_compas()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    from compas.utilities import print_profile

    main = print_profile(main)

    main()
