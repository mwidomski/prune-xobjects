import pikepdf
import argparse

#Get pdf from command line, need argument parser
#Switch for logging, need logging
#Will log errors automatically
#Can have navigation path passed on cmd line

#TODO: Better argument parsing (allow wildcards etc.)
#TODO: Custom output paths

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage= "%(prog)s File(s)...",
        description= "Remove all but largest XObject from given pdf files. For best results, make sure input pdf is uncompressed."
    )
    #parser.add_argument(
    #    "-o","--output", action="output"
    #    output =
    #)
    parser.add_argument(
        'files',nargs='*'
    )
    return parser

def main() -> None:
    #Initialize parser
    parser = init_argparse()
    args = parser.parse_args()
    #Open PDF
    for file in args.files:
        current_file = pikepdf.Pdf.open(file)
        
        #For each page in the pdf
        for page in current_file.pages:
            pagehelper = pikepdf.Page(page)
            
            #Navigate to Resources/XObject (errror if not found)
            cf_xobjects = pagehelper.resources.XObject
            
            #Loop through each entry in XObject and store the one with the maximum length
            #Other possible conditionals are whatever is /DCTDecode
            maxlength = -1
            for cf_object in cf_xobjects:
                cfo_length = cf_xobjects.get(cf_object).Length
                if cfo_length > maxlength:
                    maxlength = cfo_length
            
            #Loop through again and delete all but those ones
            #For deletion, need to use dictionary addressing as otherwise we're just deleteing the object reference
            for cf_object in cf_xobjects:
                cfo_length = cf_xobjects.get(cf_object).Length
                if cfo_length != maxlength:
                    del cf_xobjects[cf_object]
    
        #Remove unreferenced resources
        #Probably unnecessary as we're doing this backward
        current_file.remove_unreferenced_resources()
        
        #Save the pdf with compression
        save_filename = file[:-4]+"XObjectsRemoved.pdf"
        current_file.save(filename_or_stream=save_filename, object_stream_mode=pikepdf.ObjectStreamMode.generate, compress_streams=True, recompress_flate=True, encryption=False)
        
        #Close the current file
        current_file.close()

if __name__ == "__main__":
    main()
