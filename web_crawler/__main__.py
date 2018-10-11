def main():
    import web_crawler.ksrf as ksrf
    header_dictionary = ksrf.get_resolution_headers(1)
    print(header_dictionary)

main()
