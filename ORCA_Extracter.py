# This script is to be run from a folder with all the .out files and takes as arguments

#ARG1 : False/True --- To extract xyz files or not (Default False)
#ARG2 : Float --- Energy Treshold for xyz extraction (Default = 30 kJ/mol)
#ARG3 : False/True --- To extract frequencies or not (Default True)
#ARG4 : Float --- Lower frequency limit (Default = 0 cm-1)
#ARG5 : Float --- Higher frequency limit (Default = 5000 cm-1)

#Generates a file with all the relative energies sorted and extract the optimized .xyz below given energy in a separate folder and all the .frq files to plot IR Spectra in a separate folder

#External modules needed : numpy

import os
import numpy as np
import time

bash = False # To run in a Linux environment

rm_redundant_bool = False # Decide whether to remove close energy structures or not
redundant_E_treshold = 0.05 #kJ/mol relative energy difference below which two structures are considered as redundant
redundant_RMSD_treshold = 0.1 # Threshold of RMSD below which 2 structures are considered as redundant (in A)
redundant_rot_treshold = 0.0001 # Threshold of Rotational Constants dif below which 2 structures are considered as redundant

xyz = True # xyz=True to enable optimized geometry extraction
energy_treshold = 100 #kJ/mol relative energy False to extract all geometries

frq = True # frq=True to enable frequency files generation for each conformer
frq_range = [0,5000] # frq_range=[lower_lim , higher_lim] To chose the frequency range
new_scaling = True # Activate geometrical OH scaling factors (based on OH bond orientation)
scaling_factors = {'C':0.96, 'O':0.96, 'N':0.955, 'NH2s':0.962, 'NH2as':0.958, 'F':1, 'CO':0.98, 'S':1, 'H2O_free':0.96} # Dictionary with the scaling factors
H_bonds_recap = True # Generates a file with all Hbonds distances and angles

t0 = time.time()

"""
FOR BASH
"""

if bash:
    import sys
    
    dir_path = os.getcwd()
    file_names = os.listdir(dir_path)
    
    if len(sys.argv)==1:

        print('\nNo argument specified, starting the treatment...\n')
        time.sleep(1)

    elif len(sys.argv)==3:
    
        if sys.argv[1]=='n' and sys.argv[2]=='n':
    
            frq,xyz = False,False
            print('\nStarting Energy Extraction...\n')
            time.sleep(1)
    
    elif len(sys.argv)==6:
    
        frq_range[0]=float(sys.argv[2])
        frq_range[1]=float(sys.argv[3])
        energy_treshold = float(sys.argv[5])
        print(f'\nExtracting frequencies between {sys.argv[2]} and {sys.argv[3]} cm-1...\nExtracting geometries below {energy_treshold} kJ/mol...\n')
        time.sleep(2)

"""
TKINTER INTERFACE
"""

if not bash:
    import tkinter as tk
    from tkinter import filedialog
    
    root2 = tk.Tk()
    root2.attributes('-topmost', True)
    root2.withdraw()
    
    
    dir_path = filedialog.askdirectory(parent=root2, title = 'Select repertory with .out files')
    
    if dir_path:
        file_names = os.listdir(dir_path) 

    root2.destroy()
    
    # Create the main window
    root = tk.Tk()
    #root.attributes('-topmost', True)  # Make sure the window is on top
    root.focus_force()
    root.title("Your data is being treated...")
    root.geometry("750x800")
    
    # Create a Canvas widget
    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Create a Scrollbar widget
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Create a frame to hold content
    content_frame = tk.Frame(canvas)
    
    canvas.create_window((0, 0), window=content_frame, anchor="nw")
    
    # Configure the scrollbar and canvas
    canvas.config(yscrollcommand=scrollbar.set)
    
    def on_frame_configure(event):
        # Update scroll region when the content frame is resized
        canvas.config(scrollregion=canvas.bbox("all"))
    
    def update_label(text):
        global content_frame, canvas, root
    
        tk.Label(content_frame, text=text).pack(pady=5)
        canvas.yview_moveto(1.0)
        root.update()
    
    
    content_frame.bind("<Configure>", on_frame_configure)

"""
Energies extraction (Energies.txt) and convergence checking (log.txt)
"""

# Recap of the parameters in the log

if 'log.txt' in file_names:
    os.remove(dir_path + '/log.txt')

log_file = open(dir_path + '/log.txt', 'a', encoding="utf-8")

log_file.write(f'Treatment launched on {time.ctime()} in repertory {dir_path} \n\n'+
               f'Remove redundant structures : {str(rm_redundant_bool)} \n'+
               f'Treshold for redundant structures : E_ZPE <= {redundant_E_treshold} kJ/mol RMSD <= {redundant_RMSD_treshold} \n\n'+
               'Geometry extraction : '+str(xyz)+'\n')

print(f'Treatment launched on {time.ctime()} in repertory {dir_path} \n\n'+
      f'Remove redundant structures : {str(rm_redundant_bool)} \n'+
      f'Treshold for redundant structures : E_ZPE <= {redundant_E_treshold} kJ/mol RMSD <= {redundant_RMSD_treshold} \n\n'+
      'Geometry extraction : '+str(xyz))

if not bash: update_label(f'Treatment launched on {time.ctime()} in repertory {dir_path} \n\n'+
               f'Remove redundant structures : {str(rm_redundant_bool)} \n'+
               f'Treshold for redundant structures : E_ZPE <= {redundant_E_treshold} kJ/mol RMSD <= {redundant_RMSD_treshold} \n\n'+
               'Geometry extraction : '+str(xyz))

if xyz:
    log_file.write('Energy treshold for xyz extraction : '+str(energy_treshold)+' kJ/mol \n')
    print('Energy treshold for xyz extraction : '+str(energy_treshold)+' kJ/mol')
    if not bash: update_label('Energy treshold for xyz extraction : '+str(energy_treshold)+' kJ/mol')

log_file.write(' Frequency extraction : '+str(frq)+'\n')
print(' \nFrequency extraction : '+str(frq))
if not bash: update_label(' \nFrequency extraction : '+str(frq))

if frq:
    log_file.write(f'Frequency range : {frq_range[0]} cm\u207b\u00b9 → {frq_range[1]} cm\u207b\u00b9 \n')
    print(f'Frequency range : {frq_range[0]} cm\u207b\u00b9 → {frq_range[1]} cm\u207b\u00b9 ')
    if not bash: update_label(f'Frequency range : {frq_range[0]} cm\u207b\u00b9 → {frq_range[1]} cm\u207b\u00b9 ')

log_file.write(f'New scaling factors : {new_scaling}\n\n')
print(f'New scaling factors : {new_scaling}\n')
if not bash: update_label(f'New scaling factors : {new_scaling}\n')

names = []
Eelec = []
total_time = []
ZPE_list = []
G_list = []
rotational_list=[]

log_file.write('\n---- Extracting Energies ----- \n\n')
print(' ---- Extracting Energies ----- \n')
if not bash: update_label('---- Extracting Energies ----- \n')

if len(file_names)==1:
    rm_redundant_bool=False

for file_name in file_names:
    
    # Extracting convergence info, energies, calculation time and rotational constants from output file
    if file_name[-4:]=='.out' and orca: 

        log = file_name[:-4]
        file_path = dir_path + '/' + file_name
        file = open(file_path)
        content = file.read()

        if content.find('ORCA TERMINATED NORMALLY') == -1:
            log += ' --- Has Crashed \n'
            log_file.write(log)
            print(log)
            if not bash: update_label(log)
            
        elif 'THE OPTIMIZATION HAS CONVERGED' not in content and 'Single Point Calculation' not in content:
             log += ' --- Has not converged \n'
             log_file.write(log)
             print(log)
             if not bash: update_label(log)

        else:
            
            print(file_name)

            energy_index = content.rfind('FINAL SINGLE POINT ENERGY')
            energy_value = content[energy_index+30:energy_index+48]
            Eelec.append(float(energy_value))

            ZPE_index = content.find('Zero point')
            ZPE_value = float(content[ZPE_index+42:ZPE_index+52])
            ZPE_list.append(ZPE_value)

            G_index = content.rfind('Final Gibbs free energy')
            G_value = float(content[G_index+37:G_index+51])
            G_list.append(G_value)

            time_index = content.rfind('TOTAL RUN TIME')
            time_value = content[time_index+16:time_index+52]
            time_value_list = time_value.split()
            
            rotational_index = content.rfind('Rotational constants')
            rotational_value = content[rotational_index+34:rotational_index+68]
            rotational_list.append(np.array(rotational_value.split()))

            for t in time_value_list:
                if len(t)<2:
                    i=time_value_list.index(t)
                    time_value_list[i]='0'+t

            new_time_value = ':'.join(time_value_list[::2])
            total_time.append(new_time_value)

            if content.find('HURRAY') == -1:

                names.append(file_name[:-4])
                log += f' --- Did not converge in {new_time_value}\n'
                log_file.write(log)
                print(log)
                if not bash: update_label(log)

            elif content.find('HURRAY') != -1:

                names.append(file_name[:-4])
                log += f' --- Converged in {new_time_value}\n'
                log_file.write(log)
                #print(log)

        file.close()
        
    if file_name[-4:]=='.log' and gaussian:
        
        log = file_name[:-4]
        file_path = dir_path + '/' + file_name
        file = open(file_path)
        content = file.read()

        if content.find('Normal termination of Gaussian') == -1:
            log += ' --- Has Crashed \n'
            log_file.write(log)
            print(log)
            if not bash: update_label(log)
            
        elif 'Optimization completed' not in content:
             log += ' --- Has not converged \n'
             log_file.write(log)
             print(log)
             if not bash: update_label(log)

        else:
            
            print(file_name)

            energy_index = content.rfind('nuclear repulsion energy')
            energy_value = content[energy_index+30:energy_index+45]
            Eelec.append(float(energy_value))

            ZPE_index = content.find('Zero point')
            ZPE_value = float(content[ZPE_index+42:ZPE_index+52])
            ZPE_list.append(ZPE_value)
            
            G_index = content.rfind('Final Gibbs free energy')
            G_value = float(content[G_index+37:G_index+51])
            G_list.append(G_value)

            time_index = content.rfind('Job cpu time')
            time_value = content[time_index+20:time_index+60]
            time_value_list = time_value.split()
            
            rotational_index = content.rfind('Rotational constants')
            rotational_value = content[rotational_index+38:rotational_index+87]
            rotational_list.append(np.array(rotational_value.split()))

            for t in time_value_list:
                if len(t)<2:
                    i=time_value_list.index(t)
                    time_value_list[i]='0'+t

            new_time_value = ':'.join(time_value_list[::2])
            total_time.append(new_time_value)

            if content.find('Optimization completed') == -1:

                names.append(file_name[:-4])
                log += f' --- Did not converge in {new_time_value}\n'
                log_file.write(log)
                print(log)
                if not bash: update_label(log)

            elif content.find('Optimization completed') != -1:

                names.append(file_name[:-4])
                log += f' --- Converged in {new_time_value}\n'
                log_file.write(log)
                #print(log)

        file.close()
        

if 'Energies.txt' in file_names:
    os.remove(dir_path + '/Energies.txt')

log_file.close()
log_file = open(dir_path + '/log.txt', 'a', encoding="utf-8")

energy_file = open(dir_path + '/Energies.txt', 'a', encoding="utf-8")
    
E_ZPE = (np.array(Eelec) + np.array(ZPE_list)).astype(float).round(6)
relative_E_ZPE = (np.array(E_ZPE)-min(E_ZPE))*2625.5

rG_list = ((np.array(G_list)-min(G_list))*2625.5).astype(float).round(2)
G_list = np.array(G_list).astype(float).round(6)

A,B,C=np.array(rotational_list).transpose()

z = np.array([relative_E_ZPE, E_ZPE, names, total_time, rG_list, G_list, A, B, C]).transpose()

zz = np.array(sorted(z, key=lambda x: x[1], reverse=True)).transpose()

relative_E_ZPE, E_ZPE, names, total_time, rG_list, G_list, A, B, C = zz[0], zz[1], zz[2], zz[3], zz[4], zz[5], zz[6].astype(float), zz[7].astype(float), zz[8].astype(float)

rE_ZPE = relative_E_ZPE.astype(float).round(3)

def extract_xyz(filepath, energy=''):

    #Extract a xyz string variable of the optimized geometry from a ORCA5 or 6 output (.out) file


    file=open(filepath, 'r')
    lines=file.readlines()

    write=False
    write2=False

    coord_list = []

    for i,l in enumerate(lines):

        if "FINAL ENERGY EVALUATION AT THE STATIONARY POINT" in l:
            write=True
            
        elif "Single Point Calculation" in l:
            write=True

        if write and len(l.split())==4:
            write2=True
            coord_list.append(l)

        if write2 and len(l.split())!=4:
            file.close()
            break

    filename=filepath.split('/')[-1][:-4]

    text = ''
    text += str(len(coord_list))+'\n'
    text += str(energy)+' kJ/mol \n'
    text += ''.join(coord_list)

    return(text)

"""
Redundant treatment
"""

if rm_redundant_bool:

    def rmsd_kabsch(filepath1, filepath2):

        #Calculates the RMSD between two sets of coordinates using the Kabsch algorithm.

        def get_coords(xyz_str):

            lines = xyz_str.split('\n')
            num_atoms = int(lines[0])
            symbols = []
            coords = np.zeros((num_atoms, 3))
            for i in range(2, num_atoms+2):
                parts = lines[i].split()
                symbols.append(parts[0])
                coords[i-2,:] = [float(x) for x in parts[1:4]]
            return np.array(symbols), np.array(coords)

        symbols1, coords1 = get_coords(filepath1)
        symbols2, coords2 = get_coords(filepath2)

        # Remove hydrogen atoms
        heavy_atoms = np.where(symbols1 != 'H')[0]
        coords1 = coords1[heavy_atoms,:]
        coords2 = coords2[heavy_atoms,:]

        # Center the structures
        center1 = np.mean(coords1, axis=0)
        center2 = np.mean(coords2, axis=0)
        coords1 -= center1
        coords2 -= center2

        # Calculate the covariance matrix
        cov = np.dot(coords1.T, coords2)

        # Singular Value Decomposition
        u, s, v = np.linalg.svd(cov)
        d = np.linalg.det(np.dot(v.T, u.T))

        # Create the rotation matrix and translate coords1
        if d < 0:
            v[:,-1] *= -1
            d *= -1
        rot_mat = np.dot(v.T, u.T)
        coords1 = np.dot(coords1, rot_mat)

        # Calculate the RMSD
        rmsd = np.sqrt(np.sum(np.square(coords1 - coords2))/coords1.shape[0])
        return rmsd

    lja = max([len(name) for name in names])+5
    tb='ΔE+ZPE (kJ/mol)'
    ljb = len(tb)+5

    redundant_text = f'---- Redundant structures (ΔE+ZPE < {redundant_E_treshold} kJ/mol | RMSD < {redundant_RMSD_treshold}) | Rota < {redundant_rot_treshold} ---- \n\n'
    redundant_text += 'Name'.center(lja)+'|'+'Redundant with'.center(lja)+'|'+'ΔE+ZPE (kJ/mol)'.center(ljb)+'|'+'RMSD'.center(9)+'|'+'ΔA'.center(7)+'|'+'ΔB'.center(7)+'|'+'ΔC'.center(7)+'|'+'Criterium'.center(12)+'\n'

    i=1
    
    redundant_bool = False
    
    def remove_redundant(i):
        
        global E_ZPE, names, total_time, rG_list, G_list, rE_ZPE, redundant_text, A,B,C
        
        dE=str(abs(round(rE_ZPE[i-1]-rE_ZPE[i],4)))
        
        dA = round(abs(A[i-1]-A[i]),5)
        dB = round(abs(B[i-1]-B[i]),5)
        dC = round(abs(C[i-1]-C[i]),5)
        
        redundant_text += names[i-1].center(lja)+'|'+names[i].center(lja)+'|'+dE.center(ljb)+'|'+str(round(rmsd,2)).center(9) + '|' + str(dA).center(7) + '|' + str(dB).center(7) + '|' + str(dC).center(7) + '|' + crit.center(12) + '\n'
    
        EZPE_pop = list(rE_ZPE).pop(i)
        name_pop = list(names).pop(i)

        E_ZPE = np.delete(E_ZPE, i)
        names = np.delete(names, i)

        total_time = np.delete(total_time, i)
        rG_list = np.delete(rG_list, i)
        G_list = np.delete(G_list, i)
        rE_ZPE = np.delete(rE_ZPE, i)

        A,B,C=np.delete(A,i),np.delete(B,i),np.delete(C,i)
        
    while i<len(names)-1: # Through all conformers in Energy file
               
        rmsd = round(rmsd_kabsch(extract_xyz(f'{dir_path}/{names[i-1]}.out'), extract_xyz(f'{dir_path}/{names[i]}.out')), 2)
        dE_ZPE=abs(rE_ZPE[i-1]-rE_ZPE[i])
        
        dA = round(abs(A[i-1]-A[i]),5)
        dB = round(abs(B[i-1]-B[i]),5)
        dC = round(abs(C[i-1]-C[i]),5)
        
        crit = ''
        remove=False
        
        # # Criteria for removing redundant structures (E + RMSD or E + Rot)
        
        if dE_ZPE<=redundant_E_treshold and rmsd<=redundant_RMSD_treshold:
            crit += 'Energy + RMSD'
            remove=True
        
  
        if dE_ZPE<=redundant_E_treshold and dA <= redundant_rot_treshold and dB <= redundant_rot_treshold and dC <= redundant_rot_treshold:
            
            if crit=='':crit += 'Energy + Rota '
            else: crit+='+ Rota '
            
            remove=True
        
        if remove:
            remove_redundant(i)
            i-=1
    
        i+=1
        

# Writing beautifully in a file
ta = 'Name'
lja = max([len(name) for name in names])+5
energy_file.write(ta.ljust(lja))

tb='ΔE+ZPE (kJ/mol)'
ljb = len(tb)+5
energy_file.write(tb.ljust(ljb))

tc = 'E+ZPE (Ha)'
ljc = len(str(E_ZPE[0]))+5
energy_file.write(tc.ljust(ljc))


td = 'ΔG_298K (kJ/mol)'
ljd = len(td)+5
energy_file.write(td.ljust(ljd))

te = 'G_298K (Ha)'
lje = len(str(G_list[0]))+5
energy_file.write('G_298K (Ha)'.ljust(lje))

tf = 'Time (dd:hh:mm:ss)'
ljf = len(total_time[0])+5
energy_file.write(tf.ljust(ljf)+'\n')

if not bash: update_label(ta.ljust(lja)+
            tb.ljust(ljb)+tc.ljust(ljc)+
            td.ljust(ljd)+
            'G_298K (Ha)'.ljust(lje)+
            tf.ljust(ljf)+'\n')

for i in range(len(names)):
    energy_file.write(names[i].ljust(lja) +
                        str(rE_ZPE[i]).ljust(ljb) +
                        E_ZPE[i].ljust(ljc) +
                        str(rG_list[i]).ljust(ljd) +
                        str(G_list[i]).ljust(lje) +
                        total_time[i].ljust(ljf) + '\n')

    if not bash: update_label(names[i].ljust(lja) +
                        str(rE_ZPE[i]).ljust(ljb) +
                        E_ZPE[i].ljust(ljc) +
                        str(rG_list[i]).ljust(ljd) +
                        str(G_list[i]).ljust(lje) +
                        total_time[i].ljust(ljf))

energy_file.close()

log_file.write('\nEnergies extracted successfully.\n\n')
print('Energies extracted successfully.\n')
if not bash: update_label('Energies extracted successfully.\n')

if rm_redundant_bool:
    
    lr = len(redundant_text.split('\n'))-4
    redundant_text+= f'\n {lr} conformers are considered as redundant and removed from the treatment. \n'
    
    log_file.write(redundant_text)
    print(redundant_text)
    if not bash: update_label(redundant_text)
    
log_file.close()
log_file = open(dir_path + '/log.txt', 'a', encoding="utf-8")

"""
## single and multiple xyz generation (xyz_opt/*.xyz and multiple_xyz.xyz)
"""

if xyz:
    
    if os.path.exists(dir_path+'/xyz_opt'):
        for filename in os.listdir(dir_path+'/xyz_opt'):
            os.remove(dir_path+'/xyz_opt/'+filename)

    if not os.path.exists(dir_path+'/xyz_opt'):
        os.mkdir(dir_path+'/xyz_opt')

    if not os.path.exists(dir_path+'/multiple_xyz'):
        os.mkdir(dir_path+'/multiple_xyz')

    log_file.write('\n---- Extracting xyz files ----- \n\n')
    print('---- Extracting xyz files ----- \n')
    if not bash: update_label('---- Extracting xyz files -----\n')

    count=0

    text_list=[]

    energies_file = open(dir_path + '/Energies.txt')
    energy_lines = energies_file.readlines()[1:]

    for l in energy_lines:

        filename=l.split()[0]
        deltaE = float(l.split()[1])

        if deltaE > energy_treshold and energy_treshold:
            break

        filepath=dir_path + '/' + filename + '.out'
        count+=1

        name=filepath.split('/')[-1][:-4]
        filename=name+'_'+str(count)+'.xyz'

        log_file.write(str(count) + "/" + str(len(energy_lines)) + " ----- " + filename + '\n')
        print(str(count) + "/" + str(len(energy_lines)) + " ----- " + filename)
        if not bash: update_label(str(count) + "/" + str(len(energy_lines)) + " ----- " + filename)

        new_filepath=dir_path+'/xyz_opt/'+filename
        
        new_file=open(new_filepath, 'a')
        new_file.write(extract_xyz(filepath, deltaE))
        new_file.close()

        text_list.append(extract_xyz(filepath, deltaE))

    energies_file.close()

    big_text=''.join(text_list)

    base_name = '_'.join(filename.split('_')[:-2])

    multiple_xyz_file = open(dir_path+'/multiple_xyz/B3LYP_'+base_name+'_1-'+str(count)+'.xyz','w')
    multiple_xyz_file.write(big_text)
    multiple_xyz_file.close()
    
"""
## Frequencies extraction
"""

def NH2_detection(xyz): ## Detects if N is NH2 by probing 2 H closer than 1.5A in the optimized xyz; takes as entry the optimized xyz file obtained with extract_xyz
    
    NH2_indexes=[]
    xyz_lines = xyz.split('\n')
    
    for i,l in enumerate(xyz_lines[:-1]):
        
        if l.split()[0]=='N':
            count = 0
            
            vN = np.array([float(l.split()[1]), float(l.split()[2]), float(l.split()[3])])
            
            for i2,l2 in enumerate(xyz_lines[:-1]):
                
                if l2.split()[0]=='H':
                    
                    vH = np.array([float(l2.split()[1]), float(l2.split()[2]), float(l2.split()[3])])        
                        
                    n = np.linalg.norm(vN-vH)
                    
                    if n < 1.1 and count == 0:
                        count+=1
                    
                    elif n < 1.1 and count == 1:
                        NH2_indexes.append(str(i-2))
                        count=0
                
    return NH2_indexes
    
def CO_detection(xyz): ## Detects if C is CO by probing 1 O closer than 1.25A in the optimized xyz and only 3 neighbours <1.7A; takes as entry the optimized xyz file obtained with extract_xyz
    CO_indexes=[]
    xyz_lines = xyz.split('\n')
    
    for i,l in enumerate(xyz_lines[:-1]):
        
        if l.split()[0]=='C':
            count = 0
            O_neighbour = False
            vC = np.array([float(l.split()[1]), float(l.split()[2]), float(l.split()[3])])
            
            for i2,l2 in enumerate(xyz_lines[2:-1]):
                
                if l2.split()[0]=='O':
                    vO = np.array([float(l2.split()[1]), float(l2.split()[2]), float(l2.split()[3])])        
                    n = np.linalg.norm(vC-vO)
                    
                    if n < 1.25:
                        count+=1
                        O_neighbour = True
                        
                    elif n < 1.7:
                        count+=1
                        
                elif l2.split()[0]!='O' and l2!=l:
                    vX = np.array([float(l2.split()[1]), float(l2.split()[2]), float(l2.split()[3])])        
                    n = np.linalg.norm(vC-vX)
                    
                    if n<1.7:
                        count+=1
                        
            if count==3 and O_neighbour:
                CO_indexes.append(str(i-2))
                count=0
                O_neighbour=False

    return CO_indexes
    
def scaling_factors_gen(xyz):
    
    scaling_factors_OH = {}
    angles_dict={}
    distances_dict={}
    lines = xyz.split('\n')[:-1]
    
    for i,l in enumerate(lines[2:]): # 1ère boucle parcourt les O
        
        e1=l.split()[0]
        
        if e1=='O':# or e1=='N':
            
            v = l.split()[1:]
            v = np.array([float(j) for j in v])
            
            h_count=0
            h2=''
            
            for i2,l2 in enumerate(lines[2:]): # 2ème boucle parcourt les H liés aux O
                
                e2=l2.split()[0]
            
                if e2=='H':
                
                    v2=l2.split()[1:]
                    v2=np.array([float(j) for j in v2])
                    
                    d = np.linalg.norm(v2-v)
                 
                    if  d <= 1.1: # Distance limite pour liaison covalente
                        
                        #print(f'{e1}{i} - H{i2}  {round(d,2)} \u212b')

                        angles = []
                        distances = []
                        acceptors = []
                        
                        h_count +=1                    
                        free = True
                        
                        for i3, l3 in enumerate(lines[2:]): # 3ème boucle parcourt les O ou N accepteurs de liaisons H
                            
                            e3 = l3.split()[0]
                            
                            if (e3=='O' or e3=='N') and i3!=i:
                                                           
                                v3 = l3.split()[1:]
                                v3 = np.array([float(j) for j in v3])
                            
                                d2 = round(np.linalg.norm(v3-v2),2)
                                                                                         
                                if d2 <= 3.2: # Distance limite pour liaison H
                                    
                                    dot_product = np.dot(v2-v, v2-v3)
                                    cos_theta = dot_product / (d * d2)
                                    
                                    a_rad = np.arccos(cos_theta)
                                    a_deg = round(np.degrees(a_rad),1)
                                    
                                    #print(f'H{i2} - - - {e3}{i3} = {d2} \u212b')
                                    #print(f'{e1}{i}-H{i2}-{e3}{i3} = {a_deg}°')
                                    
                                    donor = e1+str(i)+h2+"-"+e2+str(i2).ljust(15-(len(e1)+len(str(i))+len(e2)+len(str(i2))+1))
                                    
                                    accept=e3+str(i3).ljust(15-(len(e3)+len(str(i3))))
                                    acceptors.append(accept)
                                    
                                    angles.append(a_deg)     
                                    distances.append(d2)                               
                                    free=False
                                    
                        if h_count == 2: # If two H are bonded to one O
                            #print(f'{e1}{i} is water!')
                            h2='b'
                            
                        donor = e1+str(i)+h2+"-"+e2+str(i2).ljust(15-(len(e1)+len(str(i))+len(e2)+len(str(i2))+1))
                        n = name.ljust(30-len(name))
            
                        if not free:
                            a,d = max(angles), distances[angles.index(max(angles))]
                            angles_dict[f'{e1}{i}{h2}']=a
                            distances_dict[f'{e1}{i}{h2}']=d
                            acceptor = acceptors[angles.index(max(angles))]
                            
                            a,d=str(a).ljust(15-len(str(a))),str(d).ljust(15-len(str(d)))
                            
                            if 'b' in n: fw.write('\n'+n+donor+acceptor+a+d) 
                            else: fw.write('\n'+n+donor+acceptor+a+d) 
                                    
                        if free:
                            
                            angles_dict[f'{e1}{i}{h2}']='f' 
                            distances_dict[f'{e1}{i}{h2}']='f' 
                            
                            a,d='f'.ljust(15-1), 'f'.ljust(15-1)
                            acceptor = 'free'.ljust(15-len('free'))
                                
                            fw.write('\n'+n+donor+acceptor+a+d)       
                            #print('Free OH')  
                            
    alpha = 7E-5
    beta = .948
        
    def f(x): 
        return alpha * x + beta   
    
    def frev(y):
        return (y - beta)/alpha
    
    for k in angles_dict.keys():
        
        try: x = 1*round(float(angles_dict[k]) - 1*float(distances_dict[k]),3)
        except: x=round(frev(0.952),3) # OH6 du man gggtt complètement libre
        
        scaling_factors_OH[k] = round(f(x),3) 

    return scaling_factors_OH

def extract_frq(filepath):

    global names, frq_range, log_file, update_label, scaling_factors, new_scaling
    
    name=filepath.split('/')[-1][:-4]
    filename=name+'.frq'
    file=open(filepath, 'r')
    char = file.read()

    # First lets take the element corresponding to each index in the output file

    elindex1 = char.rfind('LOEWDIN ATOMIC CHARGES')
    elindex2 = char.rfind('LOEWDIN REDUCED ORBITAL CHARGES')
    ellines = char[elindex1:elindex2].split('\n')
    elements_list=[]

    for line in ellines[2:-3]:
        elements_list.append(line.split()[1]+ str(int(line.split()[0]))) # Adding the index +1 next to the letter of the atom

    # Then lets extract the frequencies and corresponding intensities for each mode

    frindex1 = char.rfind('IR SPECTRUM')+217
    frindex2 = char.rfind('THERMOCHEMISTRY AT 298.15K')-267
    frlines = char[frindex1:frindex2].split('\n')

    freq_dict = {}
    modeid_list = []

    for line in frlines:
        frequency = line.split()[1]
        intensity = line.split()[3]
        if frequency not in freq_dict.keys():
            freq_dict[frequency] = intensity
        else:
            freq_dict[frequency+'0']=intensity
        modeid_list.append(int(line.split()[0][:-1]))

    # Then lets see what atoms (except H) are mostly moving for each mode with the cartesian displacement matrix

    mvindex1 = char.rfind('NORMAL MODES')+225
    mvindex2 = char.rfind('IR SPECTRUM')-14
    mvlines = char[mvindex1:mvindex2].split('\n')

    nb_atoms = len(elements_list)
    nb_modes = 3 * nb_atoms

    header_line_id = nb_modes + 1 # Removing the first 6 modes that are global translations
    header_line = mvlines[header_line_id]
    modeel_list=[]

    while len(header_line.split())>=3:

        for i,mode in enumerate(header_line.split()): # For each mode
        
            atomdisp_list=[] #Displacement norm of each atom for one mode
            disp_vect = []

            for j in range(nb_atoms):

                dx = float(mvlines[header_line_id+3*j+1].split()[i+1])
                dy = float(mvlines[header_line_id+3*j+2].split()[i+1])
                dz = float(mvlines[header_line_id+3*j+3].split()[i+1])

                v = np.array([dx,dy,dz])
                n = np.linalg.norm(v)
                
                disp_vect.append(v)
                atomdisp_list.append(n)

            tuple_list=[]
            
            for i,e in enumerate(elements_list): # makes a tuple with element name - displacement norm - displacement vector
                
                tuple_env = (elements_list[i], atomdisp_list[i], disp_vect[i])
                tuple_list.append(tuple_env)
                
            def get_disp(tup): return tup[1]
                                
            sorted_tuple_list = sorted(tuple_list, key=lambda x: (get_disp(x)), reverse=True) # sorts the nested list by displacement norm
                    
            for s in sorted_tuple_list:
                if 'H' in s[0]:
                    None
                else:
                    moving_atom_id = int(s[0][1:])
                    break
             
            modeel_list.append(moving_atom_id)

        header_line_id += nb_modes+1
        header_line = mvlines[header_line_id]

    # Finally lets write the .frq file content with the Element, Scaling Factor, Unscaled Frequency, Scaled Frequency, Intensity

    text = ''
    lja,ljb,ljc,ljd,lje = 14,24,23,21,19
    text+='Atom'.ljust(4+10) + 'Scaling_Factor'.ljust(14+10) + 'Unscaled_Freq'.ljust(13+10) + 'Scaled_Freq'.ljust(11+10) + 'Intensity'.ljust(9+10) + '\n'

    if modeid_list[0]!=6:
        ima=' has imaginary frequencies'
    
    if modeid_list[0]==6:
        ima=''
        
    Nas_bool=True
    
    NH2_id_list = NH2_detection(extract_xyz(filepath))
    CO_id_list = CO_detection(extract_xyz(filepath))
    
    trig=True
    
    if new_scaling:
        scaling_factors_OH = scaling_factors_gen(extract_xyz(filepath))

    else:
        scaling_factors_OH=[]
        
    H2O_list=[]
        
    for i in modeid_list[::-1]:
        
        i1 = i-modeid_list[0] # In case there is an imaginary frequency it will not be in the ir spectrum but still be treated in the matrix to find the moving atom
        i2 = i-6
        
        freq = float(list(freq_dict.keys())[i1])
        
        if float(freq) > frq_range[0] and float(freq) < frq_range[1]:

            atom = elements_list[modeel_list[i2]]
            
            if atom[0]=='N' and atom[1:] in NH2_id_list and Nas_bool: # Checks for NH2 to apply according scaling factors
                atom = elements_list[modeel_list[i2]]+'(as)'.ljust(lja-4)
                scaling_factor = str(scaling_factors['NH2as'])
                Nas_bool=False
                
            elif atom[0]=='N' and atom[1:] in NH2_id_list and not Nas_bool: # Checks for NH2 to apply according scaling factors
                
                if atom[1:] in NH2_id_list:
                    NH2_id_list.remove(atom[1:])
                    
                atom = elements_list[modeel_list[i2]]+'(s)'.ljust(lja-4)
                scaling_factor = str(scaling_factors['NH2s'])
                Nas_bool=True
                
            elif atom[0]=='C' and atom[1:] in CO_id_list and 1500<freq<2000:
                
                atom = elements_list[modeel_list[i2]]+'O'.ljust(lja-4)
                scaling_factor = str(scaling_factors['CO'])
            
            elif atom in scaling_factors_OH:
                
                if atom+'b' in scaling_factors_OH.keys() and atom+'b' not in H2O_list: #if free OH of water, applies a scaling factor of 'H2O free', else keep the custom function factor
                    H2O_list.append(atom+'b')
                    
                    if scaling_factors_OH[atom+'b']==0.952:
                        scaling_factor = str(scaling_factors['H2O_free'])
                        atom += 'f'
                        
                    elif scaling_factors_OH[atom]==0.952:
                        scaling_factor = str(scaling_factors['H2O_free'])
                        atom += 'f'
                        
                    else:
                       scaling_factor = str(scaling_factors_OH[atom+'b']) 
                    
                else:
                    scaling_factor = str(scaling_factors_OH[atom])    
                    atom = atom.ljust(lja-4)
                
            else:             
                scaling_factor = str(scaling_factors[atom[0]])
                atom = atom.ljust(lja-4)
                
            frequency = str(round(float(list(freq_dict.keys())[i1]),2))
            scaled_freq = str(round(float(frequency)*float(scaling_factor),2))
            intensity = list(freq_dict.values())[i1]

            text += atom.ljust(lja) + scaling_factor.ljust(ljb) + frequency.ljust(ljc) + scaled_freq.ljust(ljd) + intensity.center(lje) + '\n'
            
    log_file.write(str(list(names).index(name)+1) + '/' + str(len(names)) + " ----- " + filename + ima + '\n')
    print(str(list(names).index(name)+1) + '/' + str(len(names)) + " ----- " + filename + ima)
    if not bash: update_label(str(list(names).index(name)+1) + '/' + str(len(names)) + " ----- " + filename + ima)
    
    return(text)

if frq:

    log_file.write('\n---- Extracting Vibration Frequencies ----- \n\n')
    print('\n---- Extracting Vibration Frequencies ----- \n')
    if not bash: update_label('\n---- Extracting Vibration Frequencies -----\n')

    if not os.path.exists(dir_path+'/frq_files'):
        os.mkdir(dir_path+'/frq_files')
        
    if H_bonds_recap:
        fw_path = dir_path+'/0-H_bonds_recap.txt'
        fw = open(fw_path, 'w')
        fw.write('Molecule\t Hydroxyl_group\t linked_to\t distance(A)\t angle(°)')

    for name in names: #names is a list containing the names of all the conformers that haven't crashed

        file_path = dir_path + '/' + name + '.out'

        frq_filepath=dir_path+'/frq_files/'+name+'.frq'
        frq_file = open(frq_filepath, 'w')
        frq_file.write(extract_frq(file_path))
        frq_file.close()
        
    fw.close()
    

t1 = time.time()

dt = round(t1-t0, 2)

log_file.write('\nTotal runtime : '+str(dt)+' s\n')
print(f'\nTotal runtime : {dt} s')
if not bash: update_label(f'\nTotal runtime : {dt} s')

log_file.write('\nDone')
print('\nDone')
if not bash: update_label('\nDone')

log_file.close()

if not bash: 
    update_label('')
    root.mainloop()
    




