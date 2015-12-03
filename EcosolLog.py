# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EcosolLog
                                 A QGIS plugin
 EcosolLog
                              -------------------
        begin                : 2015-09-08
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Everton Bortolini
        email                : evertonbortolini@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
#-----------------------------------------------------------------------------------------------------------------------------
##

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
# importe algumas variaveis usadas no banco de dados
from PyQt4.QtSql import *

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from EcosolLog_dialog import EcosolLogDialog
import os.path

import psycopg2
import osgeo.ogr

#importe alguns variaveis usadas no codigo do tipo .@@@@@@@@ ("no caso para a importacao do banco de dados")
from qgis.core import *


# Variaveis globais
Ndbname = 'EcosolLog'
Nport = '5432'
Nuser = 'postgresql94'
Nhost = 'localhost'
Npassword = '*******'

##
#--------------------------------------------------------------------------------------------------------------

class EcosolLog:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'EcosolLog_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = EcosolLogDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&EcosolLog')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'EcosolLog')
        self.toolbar.setObjectName(u'EcosolLog')
	
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('EcosolLog', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    #   -----
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/EcosolLog/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'EcosolLog'),
            callback=self.run,
            parent=self.iface.mainWindow())


#--------------------------------------------------------------------------------------------
##


        #Combobox para editar produtores
        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)#("dbname = 'EcosolLog' port = '5432' user = 'postgresql94' host = 'localhost' password = 'pvb2036'")
        cur = conn.cursor()

        

        # Selecinar o nome dos centrais
        cur.execute("SELECT nome_central FROM central ORDER BY nome_central")

        # Apresentar o nome dos centrais nas comboboxs
        for nome in cur.fetchall():
            self.dlg.add_central_comboBox.addItem(nome[0]) #nome central
            self.dlg.central_produtor_comboBox.addItem(nome[0]) #nome central
            self.dlg.central_produtor_comboBox_atual.addItem(nome[0]) #nome central

        # Selecinar o nome dos produtores
        cur.execute("SELECT nome_produtor FROM produtor ORDER BY nome_produtor")

        # Apresentar o nome dos produtores nas comboboxs
        for nome in cur.fetchall():
            self.dlg.add_produtor_comboBox.addItem(nome[0]) #nome produtor
            self.dlg.produtor_comboBox.addItem(nome[0]) #nome produtor
            self.dlg.produtor_comboBox_2.addItem(nome[0]) #nome produtor

        # Selecinar o nome dos entidades
        cur.execute("SELECT nome_entidade FROM entidade ORDER BY nome_entidade")

        # Apresentar o nome dos entidades nas comboboxs
        for nome in cur.fetchall():
            self.dlg.add_entidade_comboBox.addItem(nome[0]) #nome entidade
            self.dlg.entidade_comboBox.addItem(nome[0]) #nome entidade
            self.dlg.entidade_comboBox_2.addItem(nome[0]) #nome entidade

        # Selecinar o nome dos produtos
        cur.execute("SELECT nome_produto FROM produto ORDER BY nome_produto")

        # Apresentar o nome dos produtos nas comboboxs
        for nome in cur.fetchall():
            self.dlg.prod_produtor_comboBox.addItem(nome[0]) #nome produto
            self.dlg.prod_entidade_comboBox.addItem(nome[0]) #nome produto
            self.dlg.prod_produtor_comboBox_2.addItem(nome[0]) #nome produto
            self.dlg.prod_entidade_comboBox_2.addItem(nome[0]) #nome produto



        # Atualizar a TableWidget que apresenta a tabela de central no banco de dados        
        cur.execute("SELECT nome_central, lat_central, long_central FROM central ORDER BY nome_central")
        self.dlg.central_tableWidget.setColumnCount(3)
        self.dlg.central_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.central_tableWidget.insertRow(row)
            nome1 = QTableWidgetItem(str(nome[0])) #nome central
            lati = QTableWidgetItem(str(nome[1])) #lat central
            longi = QTableWidgetItem(str(nome[2])) #long central
            self.dlg.central_tableWidget.setItem(row, 0, nome1)
            self.dlg.central_tableWidget.setItem(row, 1, lati)
            self.dlg.central_tableWidget.setItem(row, 2, longi)
            row = row + 1

        # Atualizar a TableWidget que apresenta a tabela de produto no banco de dados
        cur.execute("SELECT nome_produto, preco_produto FROM produto ORDER BY nome_produto")
        self.dlg.produto_tableWidget.setColumnCount(2)
        self.dlg.produto_tableWidget.setHorizontalHeaderLabels(['Nome', 'Preco'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.produto_tableWidget.insertRow(row)
            nome1 = QTableWidgetItem(str(nome[0]))
            preco = QTableWidgetItem(str(nome[1]))
            self.dlg.produto_tableWidget.setItem(row, 0, nome1)
            self.dlg.produto_tableWidget.setItem(row, 1, preco)
            row = row + 1

        # Atualizar a TableWidget que apresenta a tabela de produtor no banco de dados
        cur.execute("SELECT nome_produtor, lat_produtor, long_produtor FROM produtor ORDER BY nome_produtor")
        self.dlg.produtor_tableWidget.setColumnCount(3)
        self.dlg.produtor_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.produtor_tableWidget.insertRow(row)
            nome1 = QTableWidgetItem(str(nome[0]))
            lati = QTableWidgetItem(str(nome[1]))
            longi = QTableWidgetItem(str(nome[2]))
            self.dlg.produtor_tableWidget.setItem(row, 0, nome1)
            self.dlg.produtor_tableWidget.setItem(row, 1, lati)
            self.dlg.produtor_tableWidget.setItem(row, 2, longi)
            row = row + 1

        # Atualizar a TableWidget que apresenta a tabela de entidade no banco de dados
        cur.execute("SELECT nome_entidade, lat_entidade, long_entidade FROM entidade ORDER BY nome_entidade")
        self.dlg.entidade_tableWidget.setColumnCount(3)
        self.dlg.entidade_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.entidade_tableWidget.insertRow(row)
            nome1 = QTableWidgetItem(str(nome[0]))
            lati = QTableWidgetItem(str(nome[1]))
            longi = QTableWidgetItem(str(nome[2]))
            self.dlg.entidade_tableWidget.setItem(row, 0, nome1)
            self.dlg.entidade_tableWidget.setItem(row, 1, lati)
            self.dlg.entidade_tableWidget.setItem(row, 2, longi)
            row = row + 1

        # Atualizar a TableWidget que apresenta a tabela de produto produzido no banco de dados
        cur.execute("SELECT id_produtor, id_produto, tipo_produzido, tipo_potencial, data_inicio_produzido, data_fim_produzido FROM produto_produzido ORDER BY id_produto")
        self.dlg.prod_produto_tableWidget.setColumnCount(6)
        self.dlg.prod_produto_tableWidget.setHorizontalHeaderLabels(['Produtor', 'Produto', 'Produz?', 'Tem Potencial?', 'Data de Inicio', 'Data de Fim'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.prod_produto_tableWidget.insertRow(row)
            cur.execute("SELECT nome_produtor FROM produtor WHERE id_produtor = %s", [str(nome[0])])  
            for nomeb in cur.fetchall():
                produtor = nomeb[0]
            produtor = QTableWidgetItem(produtor)
            cur.execute("SELECT nome_produto FROM produto WHERE id_produto = %s", [str(nome[1])])
            for nomeb in cur.fetchall():
                produto = nomeb[0]
            produto = QTableWidgetItem(produto)
            tipo_produzido = QTableWidgetItem(str(nome[2]))
            tipo_potencial = QTableWidgetItem(str(nome[3]))
            data_inicio = QTableWidgetItem(str(nome[4]))
            data_fim = QTableWidgetItem(str(nome[5]))
            self.dlg.prod_produto_tableWidget.setItem(row, 0, produtor)
            self.dlg.prod_produto_tableWidget.setItem(row, 1, produto)
            self.dlg.prod_produto_tableWidget.setItem(row, 2, tipo_produzido)
            self.dlg.prod_produto_tableWidget.setItem(row, 3, tipo_potencial)
            self.dlg.prod_produto_tableWidget.setItem(row, 4, data_inicio)
            self.dlg.prod_produto_tableWidget.setItem(row, 5, data_fim)
            row = row + 1

        # Atualizar a TableWidget que apresenta a tabela de produto demandado no banco de dados
        cur.execute("SELECT id_entidade, id_produto, quant_demandado, data_inicio_demandado, data_fim_demandado FROM produto_demandado ORDER BY id_produto")
        self.dlg.entid_produto_tableWidget.setColumnCount(5)
        self.dlg.entid_produto_tableWidget.setHorizontalHeaderLabels(['Entidade', 'Produto', 'Quantidade', 'Data de inicio', 'Data de Fim'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.entid_produto_tableWidget.insertRow(row)
            cur.execute("SELECT nome_entidade FROM entidade WHERE id_entidade = %s", [str(nome[0])]) 
            for nomeb in cur.fetchall():
                entidade = nomeb[0]
            entidade = QTableWidgetItem(entidade)
            cur.execute("SELECT nome_produto FROM produto WHERE id_produto = %s", [str(nome[1])])
            for nomeb in cur.fetchall():
                produto = nomeb[0]
            produto = QTableWidgetItem(produto)           
            quant_entidade = QTableWidgetItem(str(nome[2]))
            data_inicio = QTableWidgetItem(str(nome[3]))
            data_fim = QTableWidgetItem(str(nome[4]))
            self.dlg.entid_produto_tableWidget.setItem(row, 0, entidade)
            self.dlg.entid_produto_tableWidget.setItem(row, 1, produto)
            self.dlg.entid_produto_tableWidget.setItem(row, 2, quant_entidade)
            self.dlg.entid_produto_tableWidget.setItem(row, 3, data_inicio)
            self.dlg.entid_produto_tableWidget.setItem(row, 4, data_fim)
            row = row + 1



        #Pushbutton para adicionar centrais
        self.dlg.add_central_pushButton.clicked.connect(self.add_central_clicked)

        #Pushbutton para atualizar centrais
        self.dlg.atual_central_pushButton.clicked.connect(self.atual_central_clicked)

        #Pushbutton para excluir centrais
        self.dlg.excluir_central_pushButton.clicked.connect(self.excluir_central_clicked)



        #Pushbutton para adicionar produtores
        self.dlg.add_produtor_pushButton.clicked.connect(self.add_produtor_clicked)

        #Pushbutton para atualizar produtores
        self.dlg.atual_prod_pushButton.clicked.connect(self.atual_prod_clicked)

        #Pushbutton para excluir produtores
        self.dlg.excluir_prod_pushButton.clicked.connect(self.excluir_prod_clicked)



        #Pushbutton para adicionar produtores
        self.dlg.add_entidade_pushButton.clicked.connect(self.add_entidade_clicked)

        #Pushbutton para atualizar produtores
        self.dlg.atual_entid_pushButton.clicked.connect(self.atual_entidade_clicked)

        #Pushbutton para excluir produtores
        self.dlg.excluir_entid_pushButton.clicked.connect(self.excluir_entidade_clicked)



        #Acessar dados da apartir de selecao da combobox
        self.dlg.add_produtor_comboBox.currentIndexChanged.connect(self.addprodutorcombobox_currentIndexChanged)

        #Acessar dados da apartir de selecao da combobox
        self.dlg.add_central_comboBox.currentIndexChanged.connect(self.addcentralcombobox_currentIndexChanged)

        #Acessar dados da apartir de selecao da combobox
        self.dlg.add_entidade_comboBox.currentIndexChanged.connect(self.addentidadecombobox_currentIndexChanged)



        #Pushbutton para adicionar produtos no produtor
        self.dlg.add_prod_produtor_pushButton.clicked.connect(self.add_prod_produtor_clicked)

        #Pushbutton para atualizar produtos no produtor
        self.dlg.atual_prod_produtor_pushButton.clicked.connect(self.atual_prod_produtor_clicked)

        #Pushbutton para excluir produtos no produtor
        self.dlg.excluir_prod_produtor_pushButton.clicked.connect(self.excluir_prod_produtor_clicked)



        #Pushbutton para adicionar produtos na entidade
        self.dlg.add_prod_entidade_pushButton.clicked.connect(self.add_prod_entidade_clicked)

        #Pushbutton para atualizar produtos na entidade
        self.dlg.atual_prod_entidade_pushButton.clicked.connect(self.atual_prod_entidade_clicked)

        #Pushbutton para excluir produtos na entidade
        self.dlg.excluir_prod_entidade_pushButton.clicked.connect(self.excluir_prod_entidade_clicked)


        #Acessar dados da apartir de selecao da combobox
        self.dlg.prod_produtor_comboBox_2.currentIndexChanged.connect(self.prod_produtorcombobox_currentIndexChanged)

        #Acessar dados da apartir de selecao da combobox
        self.dlg.prod_entidade_comboBox_2.currentIndexChanged.connect(self.prod_entidadecombobox_currentIndexChanged)


        #Processar os dados inseridos
        self.dlg.ProcessarPushButton.clicked.connect(self.ProcessarPushButton_clicked)

        # Desconectar banco de dados
        conn.commit()
        cur.close()
        conn.close()

##
#----------------------------------------------------------------------------------------------

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&EcosolLog'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()

        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:


            settings = QSettings()
            # Take the "CRS for new layers" config, overwrite it while loading layers and...
            oldProjValue = settings.value( "/Projections/defaultBehaviour", "prompt", type=str )
            settings.setValue( "/Projections/defaultBehaviour", "useProject" )

            # YOUR CODE TO LOAD THE LAYER GOES HERE

#------------------------------------------------------------------------------------------------------------------
##

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            uri = QgsDataSourceURI()
            # set host name, port, database name, username and password
            uri.setConnection("localhost", "5432", "EcosolLog", "postgresql94", "pvb2036")
            # set database schema, table name, geometry column and optionally
            # subset (WHERE clause)
            uri.setDataSource("public", "central_final", "geom_central_final", "")
            layer = QgsVectorLayer(uri.uri(), "Central", "postgres")
            QgsMapLayerRegistry.instance().addMapLayers([layer])

            # ... then set the "CRS for new layers" back
            settings.setValue( "/Projections/defaultBehaviour", oldProjValue )



            # adicionar os dados dos produtores do banco de dados para o SIG
            #QgsMapLayerRegistry.instance().removeMapLayer([layer])

            settings = QSettings()
            # Take the "CRS for new layers" config, overwrite it while loading layers and...
            oldProjValue = settings.value( "/Projections/defaultBehaviour", "prompt", type=str )
            settings.setValue( "/Projections/defaultBehaviour", "useProject" )

            # YOUR CODE TO LOAD THE LAYER GOES HERE

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            uri = QgsDataSourceURI()
            # set host name, port, database name, username and password
            uri.setConnection("localhost", "5432", "EcosolLog", "postgresql94", "pvb2036")
            # set database schema, table name, geometry column and optionally
            # subset (WHERE clause)
            uri.setDataSource("public", "produtor_final", "geom_produtor_final", "")
            layer2 = QgsVectorLayer(uri.uri(), "Produtor", "postgres")
            QgsMapLayerRegistry.instance().addMapLayers([layer2])

            # ... then set the "CRS for new layers" back
            settings.setValue( "/Projections/defaultBehaviour", oldProjValue )



            settings = QSettings()
            # Take the "CRS for new layers" config, overwrite it while loading layers and...
            oldProjValue = settings.value( "/Projections/defaultBehaviour", "prompt", type=str )
            settings.setValue( "/Projections/defaultBehaviour", "useProject" )

            # YOUR CODE TO LOAD THE LAYER GOES HERE

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            uri = QgsDataSourceURI()
            # set host name, port, database name, username and password
            uri.setConnection("localhost", "5432", "EcosolLog", "postgresql94", "pvb2036")
            # set database schema, table name, geometry column and optionally
            # subset (WHERE clause)
            uri.setDataSource("public", "entidade_final", "geom_entidade_final", "")
            layer3 = QgsVectorLayer(uri.uri(), "Entidade", "postgres")
            QgsMapLayerRegistry.instance().addMapLayers([layer3])

            # ... then set the "CRS for new layers" back
            settings.setValue( "/Projections/defaultBehaviour", oldProjValue )



            settings = QSettings()
            # Take the "CRS for new layers" config, overwrite it while loading layers and...
            oldProjValue = settings.value( "/Projections/defaultBehaviour", "prompt", type=str )
            settings.setValue( "/Projections/defaultBehaviour", "useProject" )

            # YOUR CODE TO LOAD THE LAYER GOES HERE

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            uri = QgsDataSourceURI()
            # set host name, port, database name, username and password
            uri.setConnection("localhost", "5432", "EcosolLog", "postgresql94", "pvb2036")
            # set database schema, table name, geometry column and optionally
            # subset (WHERE clause)
            uri.setDataSource("public", "fluxo_cent_enti", "geom_fluxo_cent_ent", "")
            layer4 = QgsVectorLayer(uri.uri(), "Fluxo_Central_Entidade", "postgres")
            QgsMapLayerRegistry.instance().addMapLayers([layer4])

            # ... then set the "CRS for new layers" back
            settings.setValue( "/Projections/defaultBehaviour", oldProjValue )



            settings = QSettings()
            # Take the "CRS for new layers" config, overwrite it while loading layers and...
            oldProjValue = settings.value( "/Projections/defaultBehaviour", "prompt", type=str )
            settings.setValue( "/Projections/defaultBehaviour", "useProject" )

            # YOUR CODE TO LOAD THE LAYER GOES HERE

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            uri = QgsDataSourceURI()
            # set host name, port, database name, username and password
            uri.setConnection("localhost", "5432", "EcosolLog", "postgresql94", "pvb2036")
            # set database schema, table name, geometry column and optionally
            # subset (WHERE clause)
            uri.setDataSource("public", "fluxo_prod_enti", "geom_fluxo_prod_ent", "")
            layer5 = QgsVectorLayer(uri.uri(), "Fluxo_Produtor_Entidade", "postgres")
            QgsMapLayerRegistry.instance().addMapLayers([layer5])

            # ... then set the "CRS for new layers" back
            settings.setValue( "/Projections/defaultBehaviour", oldProjValue )



    #def mechecomboboxs(self):
        

    #  -----Alimentar e carregar a tabela de centrais com seus dados basicos-----
    def add_central_clicked(self):
        
        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        try:
            # Ler valores das lines e transformar nos dados basicos dos produtores
            latitude = self.dlg.lat_central_line.text()
            longitude = self.dlg.long_central_line.text()
            latitude = float(latitude)
            longitude = float(longitude)
            nome_central = self.dlg.nome_central_line.text()

            if latitude > -90 and latitude < 90 and longitude > -180 and longitude < 180:
                # Adicionar os valores das lines no banco de dados dos produtores
                cur.execute("INSERT INTO central (nome_central,lat_central,long_central,geom_central) VALUES (%s, %s, %s, ST_GeomFromText('POINT(%s %s)'));", [nome_central, latitude, longitude, longitude, latitude])

                # Editar tabela que apresenta a tabela no banco de dados
                row = 0
                rowCount = self.dlg.central_tableWidget.rowCount()
                for row in range(rowCount):
                    self.dlg.central_tableWidget.removeRow(row)
                self.dlg.central_tableWidget.clear()
                cur.execute("SELECT nome_central, lat_central, long_central FROM central ORDER BY nome_central")
                self.dlg.central_tableWidget.setColumnCount(3)
                self.dlg.central_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
                row = 0
                for nome in cur.fetchall():
                    self.dlg.central_tableWidget.insertRow(row)
                    nome1 = QTableWidgetItem(str(nome[0]))
                    lati = QTableWidgetItem(str(nome[1]))
                    longi = QTableWidgetItem(str(nome[2]))
                    self.dlg.central_tableWidget.setItem(row, 0, nome1)
                    self.dlg.central_tableWidget.setItem(row, 1, lati)
                    self.dlg.central_tableWidget.setItem(row, 2, longi)
                    row = row + 1

                # Selecinar o nome dos centrais
                cur.execute("SELECT nome_central FROM central ORDER BY nome_central")

                # Apresentar o nome dos centrais nas comboboxs
                self.dlg.add_central_comboBox.clear()
                self.dlg.central_produtor_comboBox.clear()
                self.dlg.central_produtor_comboBox_atual.clear()
                for nome in cur.fetchall():
                    self.dlg.add_central_comboBox.addItem(nome[0]) #nome central
                    self.dlg.central_produtor_comboBox.addItem(nome[0]) #nome central
                    self.dlg.central_produtor_comboBox_atual.addItem(nome[0]) #nome central

                # Desconectar do banco de dados
                conn.commit()
                cur.close()
                conn.close()

                # Limpar lines apos adicionar os valores
                self.dlg.lat_central_line.clear()
                self.dlg.long_central_line.clear()
                self.dlg.nome_central_line.clear()

            else:
                QMessageBox.information(QWidget(), "Valor Invalido","Insira uma coordenada valida: LATITUDE entre -90 e 90 e LONGITUDE entre -180 e 180", QMessageBox.Close)

                # Limpar lines apos adicionar os valores
                self.dlg.lat_central_line.clear()
                self.dlg.long_central_line.clear()

        except ValueError:
            QMessageBox.information(QWidget(), "Valor Invalido","A LATITUDE e LONGITUDE devem ser preenchidas no seguinte formato -> 00.00000", QMessageBox.Close)
        
            # Limpar lines apos adicionar os valores
            self.dlg.lat_central_line.clear()
            self.dlg.long_central_line.clear()


    #   -----
    def atual_central_clicked(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        try:
            # Ler valores das lines e transformar nos dados basicos dos produtores
            latitude = self.dlg.lat_central_line_atual.text()
            longitude = self.dlg.long_central_line_atual.text()
            latitude = float(latitude)
            longitude = float(longitude)
            nome_central = self.dlg.add_central_comboBox.currentText()

            if latitude > -90 and latitude < 90 and longitude > -180 and longitude < 180:
                # Atualizar os valores da lines no banco de dados dos produtores
                #cur.execute.("UPDATE produtor SET geom_produtor = ST_GeomFromText('POINT(%s %s)') WHERE nome_produtor = %s", [longitude, latitude,nome_produtor]
                cur.execute("DELETE FROM central WHERE nome_central = %s", [nome_central])
                cur.execute("INSERT INTO central (nome_central,lat_central,long_central,geom_central) VALUES (%s, %s, %s, ST_GeomFromText('POINT(%s %s)'));", [nome_central, latitude, longitude, longitude, latitude])

                # Editar tabela que apresenta a tabela no banco de dados
                row = 0
                rowCount = self.dlg.central_tableWidget.rowCount()
                for row in range(rowCount):
                    self.dlg.central_tableWidget.removeRow(row)
                self.dlg.central_tableWidget.clear()
                cur.execute("SELECT nome_central, lat_central, long_central FROM central ORDER BY nome_central")
                self.dlg.central_tableWidget.setColumnCount(3)
                self.dlg.central_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
                row = 0
                for nome in cur.fetchall():
                    self.dlg.central_tableWidget.insertRow(row)
                    nome1 = QTableWidgetItem(str(nome[0]))
                    lati = QTableWidgetItem(str(nome[1]))
                    longi = QTableWidgetItem(str(nome[2]))
                    self.dlg.central_tableWidget.setItem(row, 0, nome1)
                    self.dlg.central_tableWidget.setItem(row, 1, lati)
                    self.dlg.central_tableWidget.setItem(row, 2, longi)
                    row = row + 1

                # Selecinar o nome dos centrais
                cur.execute("SELECT nome_central FROM central ORDER BY nome_central")

                # Apresentar o nome dos centrais nas comboboxs
                self.dlg.add_central_comboBox.clear()
                self.dlg.central_produtor_comboBox.clear()
                self.dlg.central_produtor_comboBox_atual.clear()
                for nome in cur.fetchall():
                    self.dlg.add_central_comboBox.addItem(nome[0]) #nome central
                    self.dlg.central_produtor_comboBox.addItem(nome[0]) #nome central
                    self.dlg.central_produtor_comboBox_atual.addItem(nome[0]) #nome central

                # Desconectar do banco de dados
                conn.commit()
                cur.close()
                conn.close()

                # Limpar lines apos adicionar os valores
                self.dlg.lat_central_line_atual.clear()
                self.dlg.long_central_line_atual.clear()

            else:
                QMessageBox.information(QWidget(), "Valor Invalido","Insira uma coordenada valida: LATITUDE entre -90 e 90 e LONGITUDE entre -180 e 180", QMessageBox.Close)

                # Limpar lines apos adicionar os valores
                self.dlg.lat_central_line_atual.clear()
                self.dlg.long_central_line_atual.clear()

        except ValueError:
            QMessageBox.information(QWidget(), "Valor Invalido","A LATITUDE e LONGITUDE devem ser preenchidas no seguinte formato -> 00.00000", QMessageBox.Close)
        
            # Limpar lines apos adicionar os valores
            self.dlg.lat_central_line_atual.clear()
            self.dlg.long_central_line_atual.clear()
        
    #   -----
    def excluir_central_clicked(self):
        
        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        # Ler valores das lines e transformar nos dados basicos dos produtores
        nome_central = self.dlg.add_central_comboBox.currentText()

        # Excluir os valores da line selecionada no banco de dados dos produtores
        cur.execute("DELETE FROM central WHERE nome_central = %s", [nome_central])

        # Editar tabela que apresenta a tabela no banco de dados
        row = 0
        rowCount = self.dlg.central_tableWidget.rowCount()
        for row in range(rowCount):
            self.dlg.central_tableWidget.removeRow(row)
        self.dlg.central_tableWidget.clear()
        cur.execute("SELECT nome_central, lat_central, long_central FROM central ORDER BY nome_central")
        self.dlg.central_tableWidget.setColumnCount(3)
        self.dlg.central_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.central_tableWidget.insertRow(row)
            nome1 = QTableWidgetItem(str(nome[0]))
            lati = QTableWidgetItem(str(nome[1]))
            longi = QTableWidgetItem(str(nome[2]))
            self.dlg.central_tableWidget.setItem(row, 0, nome1)
            self.dlg.central_tableWidget.setItem(row, 1, lati)
            self.dlg.central_tableWidget.setItem(row, 2, longi)
            row = row + 1

        # Selecinar o nome dos centrais
        cur.execute("SELECT nome_central FROM central ORDER BY nome_central")

        # Apresentar o nome dos centrais nas comboboxs
        self.dlg.add_central_comboBox.clear()
        self.dlg.central_produtor_comboBox.clear()
        self.dlg.central_produtor_comboBox_atual.clear()
        for nome in cur.fetchall():
            self.dlg.add_central_comboBox.addItem(nome[0]) #nome central
            self.dlg.central_produtor_comboBox.addItem(nome[0]) #nome central
            self.dlg.central_produtor_comboBox_atual.addItem(nome[0]) #nome central

        # Desconectar do banco de dados
        conn.commit()
        cur.close()
        conn.close()

    #  -----Alimentar e carregar a tabela de produtores com seus dados basicos-----
    def add_produtor_clicked(self):
        
        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)#("dbname = 'EcosolLog' port = '5432' user = 'postgresql94' host = 'localhost' password = 'pvb2036'")
        cur = conn.cursor()

        try:
            # Ler valores das lines e transformar nos dados basicos dos produtores
            latitude = self.dlg.lat_produtor_line.text()
            longitude = self.dlg.long_produtor_line.text()
            latitude = float(latitude)
            longitude = float(longitude)
            nome_produtor = self.dlg.nome_produtor_line.text()
            nome_central = self.dlg.central_produtor_comboBox.currentText()
            cur.execute("SELECT * FROM central WHERE nome_central = %s", [nome_central])
            for nome in cur.fetchall():        
                id_central = nome[0]

            if latitude > -90 and latitude < 90 and longitude > -180 and longitude < 180:
                # Adicionar os valores das lines no banco de dados dos produtores
                cur.execute("INSERT INTO produtor (nome_produtor,lat_produtor,long_produtor,geom_produtor,id_central) VALUES (%s, %s, %s, ST_GeomFromText('POINT(%s %s)'), %s);", [nome_produtor, latitude, longitude, longitude, latitude,id_central])

                # Editar tabela que apresenta a tabela de produtor no banco de dados
                row = 0
                rowCount = self.dlg.produtor_tableWidget.rowCount()
                for row in range(rowCount):
                    self.dlg.produtor_tableWidget.removeRow(row)
                self.dlg.produtor_tableWidget.clear()
                cur.execute("SELECT nome_produtor, lat_produtor, long_produtor FROM produtor ORDER BY nome_produtor")
                self.dlg.produtor_tableWidget.setColumnCount(3)
                self.dlg.produtor_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
                row = 0
                for nome in cur.fetchall():
                    self.dlg.produtor_tableWidget.insertRow(row)
                    nome1 = QTableWidgetItem(str(nome[0]))
                    lati = QTableWidgetItem(str(nome[1]))
                    longi = QTableWidgetItem(str(nome[2]))
                    self.dlg.produtor_tableWidget.setItem(row, 0, nome1)
                    self.dlg.produtor_tableWidget.setItem(row, 1, lati)
                    self.dlg.produtor_tableWidget.setItem(row, 2, longi)
                    row = row + 1

                # Selecinar o nome dos produtores
                cur.execute("SELECT nome_produtor FROM produtor ORDER BY nome_produtor")

                # Apresentar o nome dos produtores nas comboboxs
                self.dlg.add_produtor_comboBox.clear()
                self.dlg.produtor_comboBox.clear()
                self.dlg.produtor_comboBox_2.clear()
                for nome in cur.fetchall():
                    self.dlg.add_produtor_comboBox.addItem(nome[0]) #nome produtor
                    self.dlg.produtor_comboBox.addItem(nome[0]) #nome produtor
                    self.dlg.produtor_comboBox_2.addItem(nome[0]) #nome produtor

                # Desconectar do banco de dados
                conn.commit()
                cur.close()
                conn.close()

                # Limpar lines apos adicionar os valores
                self.dlg.lat_produtor_line.clear()
                self.dlg.long_produtor_line.clear()
                self.dlg.nome_produtor_line.clear()

            else:
                QMessageBox.information(QWidget(), "Valor Invalido","Insira uma coordenada valida: LATITUDE entre -90 e 90 e LONGITUDE entre -180 e 180", QMessageBox.Close)

                # Limpar lines apos adicionar os valores
                self.dlg.lat_produtor_line.clear()
                self.dlg.long_produtor_line.clear()

        except ValueError:
            QMessageBox.information(QWidget(), "Valor Invalido","A LATITUDE e LONGITUDE devem ser preenchidas no seguinte formato -> 00.00000", QMessageBox.Close)
        
            # Limpar lines apos adicionar os valores
            self.dlg.lat_produtor_line.clear()
            self.dlg.long_produtor_line.clear()


    #   -----
    def atual_prod_clicked(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        try:
            # Ler valores das lines e transformar nos dados basicos dos produtores
            latitude = self.dlg.lat_produtor_line_atual.text()
            longitude = self.dlg.long_produtor_line_atual.text()
            latitude = float(latitude)
            longitude = float(longitude)
            nome_produtor = self.dlg.add_produtor_comboBox.currentText()
            nome_central = self.dlg.central_produtor_comboBox_atual.currentText()
            cur.execute("SELECT * FROM central WHERE nome_central = %s", [nome_central])
            for nome in cur.fetchall():        
                id_central = nome[0]

            if latitude > -90 and latitude < 90 and longitude > -180 and longitude < 180:
                # Atualizar os valores da lines no banco de dados dos produtores
                #cur.execute.("UPDATE produtor SET geom_produtor = ST_GeomFromText('POINT(%s %s)') WHERE nome_produtor = %s", [longitude, latitude,nome_produtor]
                cur.execute("DELETE FROM produtor WHERE nome_produtor = %s", [nome_produtor])
                cur.execute("INSERT INTO produtor (nome_produtor,lat_produtor,long_produtor,geom_produtor,id_central) VALUES (%s, %s, %s, ST_GeomFromText('POINT(%s %s)'), %s);", [nome_produtor, latitude, longitude, longitude, latitude,id_central])

                # Editar tabela que apresenta a tabela de produtor no banco de dados
                row = 0
                rowCount = self.dlg.produtor_tableWidget.rowCount()
                for row in range(rowCount):
                    self.dlg.produtor_tableWidget.removeRow(row)
                self.dlg.produtor_tableWidget.clear()
                cur.execute("SELECT nome_produtor, lat_produtor, long_produtor FROM produtor ORDER BY nome_produtor")
                self.dlg.produtor_tableWidget.setColumnCount(3)
                self.dlg.produtor_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
                row = 0
                for nome in cur.fetchall():
                    self.dlg.produtor_tableWidget.insertRow(row)
                    nome1 = QTableWidgetItem(str(nome[0]))
                    lati = QTableWidgetItem(str(nome[1]))
                    longi = QTableWidgetItem(str(nome[2]))
                    self.dlg.produtor_tableWidget.setItem(row, 0, nome1)
                    self.dlg.produtor_tableWidget.setItem(row, 1, lati)
                    self.dlg.produtor_tableWidget.setItem(row, 2, longi)
                    row = row + 1

                # Selecinar o nome dos produtores
                cur.execute("SELECT nome_produtor FROM produtor ORDER BY nome_produtor")

                # Apresentar o nome dos produtores nas comboboxs
                self.dlg.add_produtor_comboBox.clear()
                self.dlg.produtor_comboBox.clear()
                self.dlg.produtor_comboBox_2.clear()
                for nome in cur.fetchall():
                    self.dlg.add_produtor_comboBox.addItem(nome[0]) #nome produtor
                    self.dlg.produtor_comboBox.addItem(nome[0]) #nome produtor
                    self.dlg.produtor_comboBox_2.addItem(nome[0]) #nome produtor

                # Desconectar do banco de dados
                conn.commit()
                cur.close()
                conn.close()

                # Limpar lines apos adicionar os valores
                self.dlg.lat_produtor_line_atual.clear()
                self.dlg.long_produtor_line_atual.clear()

            else:
                QMessageBox.information(QWidget(), "Valor Invalido","Insira uma coordenada valida: LATITUDE entre -90 e 90 e LONGITUDE entre -180 e 180", QMessageBox.Close)

                # Limpar lines apos adicionar os valores
                self.dlg.lat_produtor_line_atual.clear()
                self.dlg.long_produtor_line_atual.clear()

        except ValueError:
            QMessageBox.information(QWidget(), "Valor Invalido","A LATITUDE e LONGITUDE devem ser preenchidas no seguinte formato -> 00.00000", QMessageBox.Close)
        
            # Limpar lines apos adicionar os valores
            self.dlg.lat_produtor_line_atual.clear()
            self.dlg.long_produtor_line_atual.clear()
        
    #   -----
    def excluir_prod_clicked(self):
        
        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        # Ler valores das lines e transformar nos dados basicos dos produtores
        nome_produtor = self.dlg.add_produtor_comboBox.currentText()

        # Excluir os valores da line selecionada no banco de dados dos produtores
        cur.execute("DELETE FROM produtor WHERE nome_produtor = %s", [nome_produtor])

        # Editar tabela que apresenta a tabela de produtor no banco de dados
        row = 0
        rowCount = self.dlg.produtor_tableWidget.rowCount()
        for row in range(rowCount):
            self.dlg.produtor_tableWidget.removeRow(row)
        self.dlg.produtor_tableWidget.clear()
        cur.execute("SELECT nome_produtor, lat_produtor, long_produtor FROM produtor ORDER BY nome_produtor")
        self.dlg.produtor_tableWidget.setColumnCount(3)
        self.dlg.produtor_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.produtor_tableWidget.insertRow(row)
            nome1 = QTableWidgetItem(str(nome[0]))
            lati = QTableWidgetItem(str(nome[1]))
            longi = QTableWidgetItem(str(nome[2]))
            self.dlg.produtor_tableWidget.setItem(row, 0, nome1)
            self.dlg.produtor_tableWidget.setItem(row, 1, lati)
            self.dlg.produtor_tableWidget.setItem(row, 2, longi)
            row = row + 1

        # Selecinar o nome dos produtores
        cur.execute("SELECT nome_produtor FROM produtor ORDER BY nome_produtor")

        # Apresentar o nome dos produtores nas comboboxs
        self.dlg.add_produtor_comboBox.clear()
        self.dlg.produtor_comboBox.clear()
        self.dlg.produtor_comboBox_2.clear()
        for nome in cur.fetchall():
            self.dlg.add_produtor_comboBox.addItem(nome[0]) #nome produtor
            self.dlg.produtor_comboBox.addItem(nome[0]) #nome produtor
            self.dlg.produtor_comboBox_2.addItem(nome[0]) #nome produtor

        # Desconectar do banco de dados
        conn.commit()
        cur.close()
        conn.close()


    #  -----Alimentar e carregar a tabela de centrais com seus dados basicos-----
    def add_entidade_clicked(self):
        
        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        try:
            # Ler valores das lines e transformar nos dados basicos dos produtores
            latitude = self.dlg.lat_entidade_line.text()
            longitude = self.dlg.long_entidade_line.text()
            latitude = float(latitude)
            longitude = float(longitude)
            nome_entidade = self.dlg.nome_entidade_line.text()

            if latitude > -90 and latitude < 90 and longitude > -180 and longitude < 180:
                # Adicionar os valores das lines no banco de dados dos produtores
                cur.execute("INSERT INTO entidade (nome_entidade,lat_entidade,long_entidade,geom_entidade) VALUES (%s, %s, %s, ST_GeomFromText('POINT(%s %s)'));", [nome_entidade, latitude, longitude, longitude, latitude])

                # Editar tabela que apresenta a tabela de entidade no banco de dados
                row = 0
                rowCount = self.dlg.entidade_tableWidget.rowCount()
                for row in range(rowCount):
                    self.dlg.entidade_tableWidget.removeRow(row)
                self.dlg.entidade_tableWidget.clear()
                cur.execute("SELECT nome_entidade, lat_entidade, long_entidade FROM entidade ORDER BY nome_entidade")
                self.dlg.entidade_tableWidget.setColumnCount(3)
                self.dlg.entidade_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
                row = 0
                for nome in cur.fetchall():
                    self.dlg.entidade_tableWidget.insertRow(row)
                    nome1 = QTableWidgetItem(str(nome[0]))
                    lati = QTableWidgetItem(str(nome[1]))
                    longi = QTableWidgetItem(str(nome[2]))
                    self.dlg.entidade_tableWidget.setItem(row, 0, nome1)
                    self.dlg.entidade_tableWidget.setItem(row, 1, lati)
                    self.dlg.entidade_tableWidget.setItem(row, 2, longi)
                    row = row + 1

                # Selecinar o nome dos entidades
                cur.execute("SELECT nome_entidade FROM entidade ORDER BY nome_entidade")

                # Apresentar o nome dos entidades nas comboboxs
                self.dlg.add_entidade_comboBox.clear()
                self.dlg.entidade_comboBox.clear()
                self.dlg.entidade_comboBox_2.clear()
                for nome in cur.fetchall():
                    self.dlg.add_entidade_comboBox.addItem(nome[0]) #nome entidade
                    self.dlg.entidade_comboBox.addItem(nome[0]) #nome entidade
                    self.dlg.entidade_comboBox_2.addItem(nome[0]) #nome entidade

                # Desconectar do banco de dados
                conn.commit()
                cur.close()
                conn.close()

                # Limpar lines apos adicionar os valores
                self.dlg.lat_entidade_line.clear()
                self.dlg.long_entidade_line.clear()
                self.dlg.nome_entidade_line.clear()

            else:
                QMessageBox.information(QWidget(), "Valor Invalido","Insira uma coordenada valida: LATITUDE entre -90 e 90 e LONGITUDE entre -180 e 180", QMessageBox.Close)

                # Limpar lines apos adicionar os valores
                self.dlg.lat_entidade_line.clear()
                self.dlg.long_entidade_line.clear()

        except ValueError:
            QMessageBox.information(QWidget(), "Valor Invalido","A LATITUDE e LONGITUDE devem ser preenchidas no seguinte formato -> 00.00000", QMessageBox.Close)
        
            # Limpar lines apos adicionar os valores
            self.dlg.lat_entidade_line.clear()
            self.dlg.long_entidade_line.clear()

    #   -----
    def atual_entidade_clicked(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        try:
            # Ler valores das lines e transformar nos dados basicos dos produtores
            latitude = self.dlg.lat_entidade_line_atual.text()
            longitude = self.dlg.long_entidade_line_atual.text()
            latitude = float(latitude)
            longitude = float(longitude)
            nome_entidade = self.dlg.add_entidade_comboBox.currentText()

            if latitude > -90 and latitude < 90 and longitude > -180 and longitude < 180:
                # Atualizar os valores da lines no banco de dados dos produtores
                #cur.execute.("UPDATE produtor SET geom_produtor = ST_GeomFromText('POINT(%s %s)') WHERE nome_produtor = %s", [longitude, latitude,nome_produtor]
                cur.execute("DELETE FROM entidade WHERE nome_entidade = %s", [nome_entidade])
                cur.execute("INSERT INTO entidade (nome_entidade,lat_entidade,long_entidade,geom_entidade) VALUES (%s, %s, %s, ST_GeomFromText('POINT(%s %s)'));", [nome_entidade, latitude, longitude, longitude, latitude])

                # Editar tabela que apresenta a tabela de entidade no banco de dados
                row = 0
                rowCount = self.dlg.entidade_tableWidget.rowCount()
                for row in range(rowCount):
                    self.dlg.entidade_tableWidget.removeRow(row)
                self.dlg.entidade_tableWidget.clear()
                cur.execute("SELECT nome_entidade, lat_entidade, long_entidade FROM entidade ORDER BY nome_entidade")
                self.dlg.entidade_tableWidget.setColumnCount(3)
                self.dlg.entidade_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
                row = 0
                for nome in cur.fetchall():
                    self.dlg.entidade_tableWidget.insertRow(row)
                    nome1 = QTableWidgetItem(str(nome[0]))
                    lati = QTableWidgetItem(str(nome[1]))
                    longi = QTableWidgetItem(str(nome[2]))
                    self.dlg.entidade_tableWidget.setItem(row, 0, nome1)
                    self.dlg.entidade_tableWidget.setItem(row, 1, lati)
                    self.dlg.entidade_tableWidget.setItem(row, 2, longi)
                    row = row + 1

                # Selecinar o nome dos entidades
                cur.execute("SELECT nome_entidade FROM entidade ORDER BY nome_entidade")

                # Apresentar o nome dos entidades nas comboboxs
                self.dlg.add_entidade_comboBox.clear()
                self.dlg.entidade_comboBox.clear()
                self.dlg.entidade_comboBox_2.clear()
                for nome in cur.fetchall():
                    self.dlg.add_entidade_comboBox.addItem(nome[0]) #nome entidade
                    self.dlg.entidade_comboBox.addItem(nome[0]) #nome entidade
                    self.dlg.entidade_comboBox_2.addItem(nome[0]) #nome entidade

                # Desconectar do banco de dados
                conn.commit()
                cur.close()
                conn.close()

                # Limpar lines apos adicionar os valores
                self.dlg.lat_entidade_line_atual.clear()
                self.dlg.long_entidade_line_atual.clear()

            else:
                QMessageBox.information(QWidget(), "Valor Invalido","Insira uma coordenada valida: LATITUDE entre -90 e 90 e LONGITUDE entre -180 e 180", QMessageBox.Close)

                # Limpar lines apos adicionar os valores
                self.dlg.lat_entidade_line_atual.clear()
                self.dlg.long_entidade_line_atual.clear()

        except ValueError:
            QMessageBox.information(QWidget(), "Valor Invalido","A LATITUDE e LONGITUDE devem ser preenchidas no seguinte formato -> 00.00000", QMessageBox.Close)
        
            # Limpar lines apos adicionar os valores
            self.dlg.lat_entidade_line_atual.clear()
            self.dlg.long_entidade_line_atual.clear()

    #   -----
    def excluir_entidade_clicked(self):
        
        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        # Ler valores das lines e transformar nos dados basicos dos produtores
        nome_entidade = self.dlg.add_entidade_comboBox.currentText()

        # Excluir os valores da line selecionada no banco de dados dos produtores
        cur.execute("DELETE FROM entidade WHERE nome_entidade = %s", [nome_entidade])

        # Editar tabela que apresenta a tabela de entidade no banco de dados
        row = 0
        rowCount = self.dlg.entidade_tableWidget.rowCount()
        for row in range(rowCount):
            self.dlg.entidade_tableWidget.removeRow(row)
        self.dlg.entidade_tableWidget.clear()
        cur.execute("SELECT nome_entidade, lat_entidade, long_entidade FROM entidade ORDER BY nome_entidade")
        self.dlg.entidade_tableWidget.setColumnCount(3)
        self.dlg.entidade_tableWidget.setHorizontalHeaderLabels(['Nome', 'Latitude', 'Longitude'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.entidade_tableWidget.insertRow(row)
            nome1 = QTableWidgetItem(str(nome[0]))
            lati = QTableWidgetItem(str(nome[1]))
            longi = QTableWidgetItem(str(nome[2]))
            self.dlg.entidade_tableWidget.setItem(row, 0, nome1)
            self.dlg.entidade_tableWidget.setItem(row, 1, lati)
            self.dlg.entidade_tableWidget.setItem(row, 2, longi)
            row = row + 1

        # Selecinar o nome dos entidades
        cur.execute("SELECT nome_entidade FROM entidade ORDER BY nome_entidade")

        # Apresentar o nome dos entidades nas comboboxs
        self.dlg.add_entidade_comboBox.clear()
        self.dlg.entidade_comboBox.clear()
        self.dlg.entidade_comboBox_2.clear()
        for nome in cur.fetchall():
            self.dlg.add_entidade_comboBox.addItem(nome[0]) #nome entidade
            self.dlg.entidade_comboBox.addItem(nome[0]) #nome entidade
            self.dlg.entidade_comboBox_2.addItem(nome[0]) #nome entidade

        # Desconectar do banco de dados
        conn.commit()
        cur.close()
        conn.close()


    #   -----
    def addcentralcombobox_currentIndexChanged(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()
 
        nome_central_selec = str(self.dlg.add_central_comboBox.currentText())

        # Selecinar o nome dos produtores
        cur.execute("SELECT lat_central, long_central FROM central WHERE nome_central = %s", [nome_central_selec])
        for nome1 in cur.fetchall():        
            self.dlg.lat_central_line_atual.setText(str(nome1[0]))
            self.dlg.long_central_line_atual.setText(str(nome1[1]))

        # Desconectar banco de dados
        conn.commit()
        cur.close()
        conn.close()


    #   -----
    def addprodutorcombobox_currentIndexChanged(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)#("dbname = 'EcosolLog' port = '5432' user = 'postgresql94' host = 'localhost' password = 'pvb2036'")
        cur = conn.cursor()
 
        # Selecinar o nome dos produtores
        cur.execute("SELECT * FROM produtor ORDER BY nome_produtor")
        nome_produtor_selec = str(self.dlg.add_produtor_comboBox.currentText())

        # Selecinar o nome dos produtores
        cur.execute("SELECT lat_produtor, long_produtor FROM produtor WHERE nome_produtor = %s", [nome_produtor_selec])
        for nome in cur.fetchall():        
            self.dlg.lat_produtor_line_atual.setText(str(nome[0]))
            self.dlg.long_produtor_line_atual.setText(str(nome[1]))

        # Desconectar banco de dados
        conn.commit()
        cur.close()
        conn.close()


    #   -----
    def addentidadecombobox_currentIndexChanged(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()
 
        nome_entidade_selec = str(self.dlg.add_entidade_comboBox.currentText())

        # Selecinar o nome dos produtores
        cur.execute("SELECT lat_entidade, long_entidade FROM entidade WHERE nome_entidade = %s", [nome_entidade_selec])
        for nome in cur.fetchall():        
            self.dlg.lat_entidade_line_atual.setText(str(nome[0]))
            self.dlg.long_entidade_line_atual.setText(str(nome[1]))

        # Desconectar banco de dados
        conn.commit()
        cur.close()
        conn.close()


    #   -----
    def add_prod_produtor_clicked(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        # Ler valores das lines e transformar nos dados basicos dos produtores
        nome_produtor_selec = str(self.dlg.produtor_comboBox.currentText())
        cur.execute("SELECT id_produtor FROM produtor WHERE nome_produtor = %s", [nome_produtor_selec])
        for nome in cur.fetchall():        
            id_produtor = nome[0]

        nome_produto_selec = str(self.dlg.prod_produtor_comboBox.currentText())
        cur.execute("SELECT id_produto FROM produto WHERE nome_produto = %s", [nome_produto_selec])
        for nome in cur.fetchall():        
            id_produto = nome[0]

        if self.dlg.produz_checkBox.isChecked():
            tipo_produzido = True
        else:
            tipo_produzido = False

        if self.dlg.potencial_checkBox.isChecked():
            tipo_potencial = True
        else:
            tipo_potencial = False

        data_inicio = self.dlg.prod_inicio_dateEdit.date().toString("dd-MM-yyyy")
        data_fim = self.dlg.prod_fim_dateEdit.date().toString("dd-MM-yyyy")

        # Adicionar os valores das lines no banco de dados dos produtores
        cur.execute("INSERT INTO produto_produzido (id_produtor,id_produto,tipo_produzido,tipo_potencial,data_inicio_produzido,data_fim_produzido) VALUES (%s, %s, %s, %s, %s,%s);", [id_produtor, id_produto, tipo_produzido, tipo_potencial, data_inicio, data_fim])

        # Atualizar a TableWidget que apresenta a tabela de produto produzido no banco de dados
        row = 0
        rowCount = self.dlg.prod_produto_tableWidget.rowCount()
        for row in range(rowCount):
            self.dlg.prod_produto_tableWidget.removeRow(row)
        self.dlg.prod_produto_tableWidget.clear()
        cur.execute("SELECT id_produtor, id_produto, tipo_produzido, tipo_potencial, data_inicio_produzido, data_fim_produzido FROM produto_produzido ORDER BY id_produto")
        self.dlg.prod_produto_tableWidget.setColumnCount(6)
        self.dlg.prod_produto_tableWidget.setHorizontalHeaderLabels(['Produtor', 'Produto', 'Produz?', 'Tem Potencial', 'Data de Inicio', 'Data de Fim'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.prod_produto_tableWidget.insertRow(row)
            cur.execute("SELECT nome_produtor FROM produtor WHERE id_produtor = %s", [str(nome[0])])  
            for nomeb in cur.fetchall():
                produtor = nomeb[0]
            produtor = QTableWidgetItem(produtor)
            cur.execute("SELECT nome_produto FROM produto WHERE id_produto = %s", [str(nome[1])])
            for nomeb in cur.fetchall():
                produto = nomeb[0]
            produto = QTableWidgetItem(produto)
            tipo_produzido = QTableWidgetItem(str(nome[2]))
            tipo_potencial = QTableWidgetItem(str(nome[3]))
            data_inicio = QTableWidgetItem(str(nome[4]))
            data_fim = QTableWidgetItem(str(nome[5]))
            self.dlg.prod_produto_tableWidget.setItem(row, 0, produtor)
            self.dlg.prod_produto_tableWidget.setItem(row, 1, produto)
            self.dlg.prod_produto_tableWidget.setItem(row, 2, tipo_produzido)
            self.dlg.prod_produto_tableWidget.setItem(row, 3, tipo_potencial)
            self.dlg.prod_produto_tableWidget.setItem(row, 4, data_inicio)
            self.dlg.prod_produto_tableWidget.setItem(row, 5, data_fim)
            row = row + 1

        # Desconectar banco de dados
        conn.commit()
        cur.close()
        conn.close()
        

    #   -----
    def atual_prod_produtor_clicked(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        # Ler valores das lines e transformar nos dados basicos dos produtores
        nome_produtor_selec = str(self.dlg.produtor_comboBox_2.currentText())
        cur.execute("SELECT id_produtor FROM produtor WHERE nome_produtor = %s", [nome_produtor_selec])
        for nome in cur.fetchall():        
            id_produtor = nome[0]

        nome_produto_selec = str(self.dlg.prod_produtor_comboBox_2.currentText())
        cur.execute("SELECT id_produto FROM produto WHERE nome_produto = %s", [nome_produto_selec])
        for nome in cur.fetchall():        
            id_produto = nome[0]

        if self.dlg.produz_checkBox_2.isChecked():
            tipo_produzido = True
        else:
            tipo_produzido = False

        if self.dlg.potencial_checkBox_2.isChecked():
            tipo_potencial = True
        else:
            tipo_potencial = False

        data_inicio = self.dlg.prod_inicio_dateEdit_2.date().toString("dd-MM-yyyy")
        data_fim = self.dlg.prod_fim_dateEdit_2.date().toString("dd-MM-yyyy")

        # Adicionar os valores das lines no banco de dados dos produtores
        cur.execute("DELETE FROM produto_produzido WHERE id_produtor = %s AND id_produto = %s", [id_produtor,id_produto])
        cur.execute("INSERT INTO produto_produzido(id_produtor, id_produto, tipo_produzido, tipo_potencial, data_inicio_produzido, data_fim_produzido) VALUES (%s, %s, %s, %s, %s,%s);", [id_produtor, id_produto, tipo_produzido, tipo_potencial, data_inicio, data_fim])

        # Atualizar a TableWidget que apresenta a tabela de produto produzido no banco de dados
        row = 0
        rowCount = self.dlg.prod_produto_tableWidget.rowCount()
        for row in range(rowCount):
            self.dlg.prod_produto_tableWidget.removeRow(row)
        self.dlg.prod_produto_tableWidget.clear()
        cur.execute("SELECT id_produtor, id_produto, tipo_produzido, tipo_potencial, data_inicio_produzido, data_fim_produzido FROM produto_produzido ORDER BY id_produto")
        self.dlg.prod_produto_tableWidget.setColumnCount(6)
        self.dlg.prod_produto_tableWidget.setHorizontalHeaderLabels(['Produtor', 'Produto', 'Produz?', 'Tem Potencial', 'Data de Inicio', 'Data de Fim'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.prod_produto_tableWidget.insertRow(row)
            cur.execute("SELECT nome_produtor FROM produtor WHERE id_produtor = %s", [str(nome[0])])  
            for nomeb in cur.fetchall():
                produtor = nomeb[0]
            produtor = QTableWidgetItem(produtor)
            cur.execute("SELECT nome_produto FROM produto WHERE id_produto = %s", [str(nome[1])])
            for nomeb in cur.fetchall():
                produto = nomeb[0]
            produto = QTableWidgetItem(produto)
            tipo_produzido = QTableWidgetItem(str(nome[2]))
            tipo_potencial = QTableWidgetItem(str(nome[3]))
            data_inicio = QTableWidgetItem(str(nome[4]))
            data_fim = QTableWidgetItem(str(nome[5]))
            self.dlg.prod_produto_tableWidget.setItem(row, 0, produtor)
            self.dlg.prod_produto_tableWidget.setItem(row, 1, produto)
            self.dlg.prod_produto_tableWidget.setItem(row, 2, tipo_produzido)
            self.dlg.prod_produto_tableWidget.setItem(row, 3, tipo_potencial)
            self.dlg.prod_produto_tableWidget.setItem(row, 4, data_inicio)
            self.dlg.prod_produto_tableWidget.setItem(row, 5, data_fim)
            row = row + 1

        # Desconectar banco de dados
        conn.commit()
        cur.close()
        conn.close()


    #   -----
    def excluir_prod_produtor_clicked(self):
        
        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        # Ler valores das lines e transformar nos dados basicos dos produtores
        nome_produtor_selec = str(self.dlg.produtor_comboBox_2.currentText())
        cur.execute("SELECT id_produtor FROM produtor WHERE nome_produtor = %s", [nome_produtor_selec])
        for nome in cur.fetchall():        
            id_produtor = nome[0]

        nome_produto_selec = str(self.dlg.prod_produtor_comboBox_2.currentText())
        cur.execute("SELECT id_produto FROM produto WHERE nome_produto = %s", [nome_produto_selec])
        for nome in cur.fetchall():        
            id_produto = nome[0]

        # Excluir os valores da line selecionada no banco de dados dos produtores
        cur.execute("DELETE FROM produto_produzido WHERE id_produtor = %s AND id_produto = %s", [id_produtor,id_produto])

        # Atualizar a TableWidget que apresenta a tabela de produto produzido no banco de dados
        row = 0
        rowCount = self.dlg.prod_produto_tableWidget.rowCount()
        for row in range(rowCount):
            self.dlg.prod_produto_tableWidget.removeRow(row)
        self.dlg.prod_produto_tableWidget.clear()
        cur.execute("SELECT id_produtor, id_produto, tipo_produzido, tipo_potencial, data_inicio_produzido, data_fim_produzido FROM produto_produzido ORDER BY id_produto")
        self.dlg.prod_produto_tableWidget.setColumnCount(6)
        self.dlg.prod_produto_tableWidget.setHorizontalHeaderLabels(['Produtor', 'Produto', 'Produz?', 'Tem Potencial', 'Data de Inicio', 'Data de Fim'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.prod_produto_tableWidget.insertRow(row)
            cur.execute("SELECT nome_produtor FROM produtor WHERE id_produtor = %s", [str(nome[0])])  
            for nomeb in cur.fetchall():
                produtor = nomeb[0]
            produtor = QTableWidgetItem(produtor)
            cur.execute("SELECT nome_produto FROM produto WHERE id_produto = %s", [str(nome[1])])
            for nomeb in cur.fetchall():
                produto = nomeb[0]
            produto = QTableWidgetItem(produto)
            tipo_produzido = QTableWidgetItem(str(nome[2]))
            tipo_potencial = QTableWidgetItem(str(nome[3]))
            data_inicio = QTableWidgetItem(str(nome[4]))
            data_fim = QTableWidgetItem(str(nome[5]))
            self.dlg.prod_produto_tableWidget.setItem(row, 0, produtor)
            self.dlg.prod_produto_tableWidget.setItem(row, 1, produto)
            self.dlg.prod_produto_tableWidget.setItem(row, 2, tipo_produzido)
            self.dlg.prod_produto_tableWidget.setItem(row, 3, tipo_potencial)
            self.dlg.prod_produto_tableWidget.setItem(row, 4, data_inicio)
            self.dlg.prod_produto_tableWidget.setItem(row, 5, data_fim)
            row = row + 1

        # Desconectar do banco de dados
        conn.commit()
        cur.close()
        conn.close()



    #   -----
    def add_prod_entidade_clicked(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        try:
            # Ler valores das lines e transformar nos dados basicos dos produtores
            nome_entidade_selec = str(self.dlg.entidade_comboBox.currentText())
            cur.execute("SELECT id_entidade FROM entidade WHERE nome_entidade = %s", [nome_entidade_selec])
            for nome in cur.fetchall():        
                id_entidade = nome[0]

            nome_produto_selec = str(self.dlg.prod_entidade_comboBox.currentText())
            cur.execute("SELECT id_produto FROM produto WHERE nome_produto = %s", [nome_produto_selec])
            for nome in cur.fetchall():        
                id_produto = nome[0]

            quant_entidade = self.dlg.quant_entidade_lineEdit.text()
            data_inicio = self.dlg.demanda_inicio_dateEdit.date().toString("dd-MM-yyyy")
            data_fim = self.dlg.demanda_fim_dateEdit.date().toString("dd-MM-yyyy")

            # Adicionar os valores das lines no banco de dados dos produtores
            cur.execute("INSERT INTO produto_demandado (id_entidade,id_produto,quant_demandado,data_inicio_demandado,data_fim_demandado) VALUES (%s, %s, %s, %s, %s);", [id_entidade, id_produto, quant_entidade, data_inicio, data_fim])

            # Atualizar a TableWidget que apresenta a tabela de produto demandado no banco de dados
            row = 0
            rowCount = self.dlg.entid_produto_tableWidget.rowCount()
            for row in range(rowCount):
                self.dlg.entid_produto_tableWidget.removeRow(row)
            self.dlg.entid_produto_tableWidget.clear()
            cur.execute("SELECT id_entidade, id_produto, quant_demandado, data_inicio_demandado, data_fim_demandado FROM produto_demandado ORDER BY id_produto")
            self.dlg.entid_produto_tableWidget.setColumnCount(5)
            self.dlg.entid_produto_tableWidget.setHorizontalHeaderLabels(['Entidade', 'Produto', 'Quantidade', 'Data de inicio', 'Data de Fim'])
            row = 0
            for nome in cur.fetchall():
                self.dlg.entid_produto_tableWidget.insertRow(row)
                cur.execute("SELECT nome_entidade FROM entidade WHERE id_entidade = %s", [str(nome[0])]) 
                for nomeb in cur.fetchall():
                    entidade = nomeb[0]
                entidade = QTableWidgetItem(entidade)
                cur.execute("SELECT nome_produto FROM produto WHERE id_produto = %s", [str(nome[1])])
                for nomeb in cur.fetchall():
                    produto = nomeb[0]
                produto = QTableWidgetItem(produto)
                quant_entidade = QTableWidgetItem(str(nome[2]))
                data_inicio = QTableWidgetItem(str(nome[3]))
                data_fim = QTableWidgetItem(str(nome[4]))
                self.dlg.entid_produto_tableWidget.setItem(row, 0, entidade)
                self.dlg.entid_produto_tableWidget.setItem(row, 1, produto)
                self.dlg.entid_produto_tableWidget.setItem(row, 2, quant_entidade)
                self.dlg.entid_produto_tableWidget.setItem(row, 3, data_inicio)
                self.dlg.entid_produto_tableWidget.setItem(row, 4, data_fim)
                row = row + 1

            # Desconectar banco de dados
            conn.commit()
            cur.close()
            conn.close()

            self.dlg.quant_entidade_lineEdit.clear()

        except ValueError:
            QMessageBox.information(QWidget(), "Valor Invalido","A QUANTIDADE DE PRODUTO deve ser preenchida como NUMERO", QMessageBox.Close)

        self.dlg.quant_entidade_lineEdit.text()

    #   -----
    def atual_prod_entidade_clicked(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        try:
            # Ler valores das lines e transformar nos dados basicos dos produtores
            nome_entidade_selec = str(self.dlg.entidade_comboBox_2.currentText())
            cur.execute("SELECT id_entidade FROM entidade WHERE nome_entidade = %s", [nome_entidade_selec])
            for nome in cur.fetchall():
                id_entidade = nome[0]

            nome_produto_selec = str(self.dlg.prod_entidade_comboBox_2.currentText())
            cur.execute("SELECT id_produto FROM produto WHERE nome_produto = %s", [nome_produto_selec])
            for nome in cur.fetchall():
                id_produto = nome[0]

            quant_entidade = self.dlg.quant_entidade_lineEdit_2.text()
            data_inicio = self.dlg.demanda_inicio_dateEdit_2.date().toString("dd-MM-yyyy")
            data_fim = self.dlg.demanda_fim_dateEdit_2.date().toString("dd-MM-yyyy")

            # Adicionar os valores das lines no banco de dados dos produtores
            cur.execute("DELETE FROM produto_demandado WHERE id_entidade = %s AND id_produto = %s", [id_entidade,id_produto])
            cur.execute("INSERT INTO produto_demandado (id_entidade,id_produto,quant_demandado,data_inicio_demandado,data_fim_demandado) VALUES (%s, %s, %s, %s, %s);", [id_entidade, id_produto, quant_entidade, data_inicio, data_fim])

            # Atualizar a TableWidget que apresenta a tabela de produto demandado no banco de dados
            row = 0
            rowCount = self.dlg.entid_produto_tableWidget.rowCount()
            for row in range(rowCount):
                self.dlg.entid_produto_tableWidget.removeRow(row)
            self.dlg.entid_produto_tableWidget.clear()
            cur.execute("SELECT id_entidade, id_produto, quant_demandado, data_inicio_demandado, data_fim_demandado FROM produto_demandado ORDER BY id_produto")
            self.dlg.entid_produto_tableWidget.setColumnCount(5)
            self.dlg.entid_produto_tableWidget.setHorizontalHeaderLabels(['Entidade', 'Produto', 'Quantidade', 'Data de inicio', 'Data de Fim'])
            row = 0
            for nome in cur.fetchall():
                self.dlg.entid_produto_tableWidget.insertRow(row)
                cur.execute("SELECT nome_entidade FROM entidade WHERE id_entidade = %s", [str(nome[0])]) 
                for nomeb in cur.fetchall():
                    entidade = nomeb[0]
                entidade = QTableWidgetItem(entidade)
                cur.execute("SELECT nome_produto FROM produto WHERE id_produto = %s", [str(nome[1])])
                for nomeb in cur.fetchall():
                    produto = nomeb[0]
                produto = QTableWidgetItem(produto)
                quant_entidade = QTableWidgetItem(str(nome[2]))
                data_inicio = QTableWidgetItem(str(nome[3]))
                data_fim = QTableWidgetItem(str(nome[4]))
                self.dlg.entid_produto_tableWidget.setItem(row, 0, entidade)
                self.dlg.entid_produto_tableWidget.setItem(row, 1, produto)
                self.dlg.entid_produto_tableWidget.setItem(row, 2, quant_entidade)
                self.dlg.entid_produto_tableWidget.setItem(row, 3, data_inicio)
                self.dlg.entid_produto_tableWidget.setItem(row, 4, data_fim)
                row = row + 1

            # Desconectar banco de dados
            conn.commit()
            cur.close()
            conn.close()

            self.dlg.quant_entidade_lineEdit_2.clear()

        except ValueError:
            QMessageBox.information(QWidget(), "Valor Invalido","A QUANTIDADE DE PRODUTO deve ser preenchida como NUMERO", QMessageBox.Close)

        self.dlg.quant_entidade_lineEdit_2.text()


    #   -----
    def excluir_prod_entidade_clicked(self):
        
        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        # Ler valores das lines e transformar nos dados basicos dos produtores
        nome_produtor_selec = str(self.dlg.produtor_comboBox_2.currentText())
        cur.execute("SELECT id_produtor FROM produtor WHERE nome_produtor = %s", [nome_produtor_selec])
        for nome in cur.fetchall():        
            id_produtor = nome[0]

        nome_produto_selec = str(self.dlg.prod_produtor_comboBox_2.currentText())
        cur.execute("SELECT id_produto FROM produto WHERE nome_produto = %s", [nome_produto_selec])
        for nome in cur.fetchall():        
            id_produto = nome[0]

        # Excluir os valores da line selecionada no banco de dados dos produtores
        cur.execute("DELETE FROM produto_demandado WHERE id_entidade = %s AND id_produto = %s", [id_produtor,id_produto])

        # Atualizar a TableWidget que apresenta a tabela de produto demandado no banco de dados
        row = 0
        rowCount = self.dlg.entid_produto_tableWidget.rowCount()
        for row in range(rowCount):
            self.dlg.entid_produto_tableWidget.removeRow(row)
        self.dlg.entid_produto_tableWidget.clear()
        cur.execute("SELECT id_entidade, id_produto, quant_demandado, data_inicio_demandado, data_fim_demandado FROM produto_demandado ORDER BY id_produto")
        self.dlg.entid_produto_tableWidget.setColumnCount(5)
        self.dlg.entid_produto_tableWidget.setHorizontalHeaderLabels(['Entidade', 'Produto', 'Quantidade', 'Data de inicio', 'Data de Fim'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.entid_produto_tableWidget.insertRow(row)
            cur.execute("SELECT nome_entidade FROM entidade WHERE id_entidade = %s", [str(nome[0])]) 
            for nomeb in cur.fetchall():
                entidade = nomeb[0]
            entidade = QTableWidgetItem(entidade)
            cur.execute("SELECT nome_produto FROM produto WHERE id_produto = %s", [str(nome[1])])
            for nomeb in cur.fetchall():
                produto = nomeb[0]
            quant_entidade = QTableWidgetItem(str(nome[2]))
            data_inicio = QTableWidgetItem(str(nome[3]))
            data_fim = QTableWidgetItem(str(nome[4]))
            self.dlg.entid_produto_tableWidget.setItem(row, 0, entidade)
            self.dlg.entid_produto_tableWidget.setItem(row, 1, produto)
            self.dlg.entid_produto_tableWidget.setItem(row, 2, quant_entidade)
            self.dlg.entid_produto_tableWidget.setItem(row, 3, data_inicio)
            self.dlg.entid_produto_tableWidget.setItem(row, 4, data_fim)
            row = row + 1

        # Desconectar do banco de dados
        conn.commit()
        cur.close()
        conn.close()

    #    -----
    def prod_produtorcombobox_currentIndexChanged(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)#("dbname = 'EcosolLog' port = '5432' user = 'postgresql94' host = 'localhost' password = 'pvb2036'")
        cur = conn.cursor()

        # Postar valores das lines e transformar nos dados basicos dos produtores
        nome_produtor_selec = str(self.dlg.produtor_comboBox_2.currentText())
        cur.execute("SELECT id_produtor FROM produtor WHERE nome_produtor = %s", [nome_produtor_selec])
        for nome in cur.fetchall():        
            id_produtor = nome[0]

        nome_produto_selec = str(self.dlg.prod_produtor_comboBox_2.currentText())
        cur.execute("SELECT id_produto FROM produto WHERE nome_produto = %s", [nome_produto_selec])
        for nome in cur.fetchall():        
            id_produto = nome[0]

        cur.execute("SELECT tipo_produzido, tipo_potencial, data_inicio_produzido, data_fim_produzido FROM produto_produzido WHERE id_produtor = %s AND id_produto = %s", [id_produtor,id_produto])
        for nome in cur.fetchall():
            tipo_produzido = nome[0]
            tipo_potencial = nome[1]
            data_inicio = nome[2]
            data_fim = nome[3]

            self.dlg.produz_checkBox_2.setChecked(tipo_produzido)
            self.dlg.potencial_checkBox_2.setChecked(tipo_potencial)
            self.dlg.prod_inicio_dateEdit_2.setDate(data_inicio)
            self.dlg.prod_fim_dateEdit_2.setDate(data_fim)

        # Desconectar do banco de dados
        conn.commit()
        cur.close()
        conn.close()

    #    -----
    def prod_entidadecombobox_currentIndexChanged(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

        # Ler valores das lines e transformar nos dados basicos dos produtores
        nome_entidade_selec = str(self.dlg.entidade_comboBox_2.currentText())
        cur.execute("SELECT id_entidade FROM entidade WHERE nome_entidade = %s", [nome_entidade_selec])
        for nome in cur.fetchall():
            id_entidade = nome[0]

        nome_produto_selec = str(self.dlg.prod_entidade_comboBox_2.currentText())
        cur.execute("SELECT id_produto FROM produto WHERE nome_produto = %s", [nome_produto_selec])
        for nome in cur.fetchall():
            id_produto = nome[0]

        cur.execute("SELECT quant_demandado, data_inicio_demandado, data_fim_demandado FROM produto_demandado WHERE id_entidade = %s AND id_produto = %s", [id_entidade,id_produto])
        for nome in cur.fetchall():
            quant_entidade = nome[0]
            data_inicio = nome[1]
            data_fim = nome[2]

            self.dlg.quant_entidade_lineEdit_2.setText(str(quant_entidade))
            self.dlg.demanda_inicio_dateEdit_2.setDate(data_inicio)
            self.dlg.demanda_fim_dateEdit_2.setDate(data_fim)

        # Desconectar do banco de dados
        conn.commit()
        cur.close()
        conn.close()

    #    -----
    def ProcessarPushButton_clicked(self):

        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname = Ndbname, port = Nport, user = Nuser, host = Nhost, password = Npassword)
        cur = conn.cursor()

#-------
        #Distancia = {'nome_produtor': [], 'nome_entidade':[], 'distancia':[]}
        #Produzido = {'nome_produtor': [], 'nome_produto':[]}
        #Demandado = {'nome_entidade': [], 'nome_produto':[], 'quant_demandado': [], 'preco_produto':[], 'preco_total':[]}
        #Produtor = {'nome_produtor': [], 'saldo':[]}
        
#        cur.execute("SELECT nome_produtor, nome_entidade, ST_Distance_Sphere(produtor.geom_produtor, entidade.geom_entidade)/1000 AS distancia, ST_MakeLine(produtor.geom_produtor, entidade.geom_entidade) FROM produtor, entidade ORDER BY distancia")
      
#        Distancia = cur.fetchone()
        #for nome in cur.fetchall():
            # --- Distancia['nome_produtor'].append(nome(0))
            #Distancia.['nome_produtor'] = nome[0]
            #Distancia.update({'nome_produtor': nome(0)})
            #Distancia['nome_entidade'].append(nome(1))
            #Distancia['distancia'].append(nome(2))
        
#        cur.execute("SELECT nome_produtor, nome_produto FROM produtor, produto, produto_produzido WHERE produtor.id_produtor = produto_produzido.id_produtor AND produto.id_produto = produto_produzido.id_produto AND produto_produzido.tipo_produzido = 'true' ORDER BY nome_produtor")
            
#        Produzido = cur.fetchone()
        #for nome in cur.fetchall():
            #Produzido['nome_produtor'].append(nome(0))
            #Produzido['nome_produto'].append(nome(1))

#        cur.execute("SELECT nome_entidade, nome_produto, quant_demandado, preco_produto, quant_demandado*preco_produto AS preco_total FROM produto, entidade, produto_demandado WHERE produto.id_produto = produto_demandado.id_produto AND entidade.id_entidade = produto_demandado.id_entidade ORDER BY preco_total")

#        Demandado = cur.fetchone()
        #for nome in cur.fetchall():
            #Demandado['nome_entidade'].append(nome(0))
            #Demandado['nome_produto'].append(nome(1))
            #Demandado['quant_demandado'].append(nome(2))
            #Demandado['preco_produto'].append(nome(3))
            #Demandado['preco_total'].append(nome(4))

#        cur.execute("SELECT nome_produtor FROM produtor ORDER BY nome_produtor")

#        Produtor = cur.fetchone()
        #for nome in cur.fetchall():
            #Produtor['nome_produtor'].append(nome(0))
            #Produtor['nome_produtor'].append(0)

        #length_Distancia = {key: len(value) for key, value in d.items()}
        #length_nome_produtor = length_dict['key']
        #lengths = [len(v) for v in d.values()]


        #for x in len(Distancia['nome_produtor']):
#        for x in enumerate(Distancia):
#            produtor = Distancia['nome_produtor'[x]]
#            entidade = Distancia['nome_entidade'[x]]

#            for y in len(Produzido):
#                if Produzido['nome_produtor'] == produtor:
#                    produto = Produzido[('nome_produto'[y]]
                    
#                    for z in len(Demandado):
#                        if Demandado['nome_entidade'] == nome_entidade and Demandado['nome_produto'] == nome_produto:
#                            Demandado ['quant_demandado'[z]]                         
#                            Demandado ['preco_total'[z]]       

            #match = l
                #break
            #else:
                #match = None
#-------

        cur.execute("DELETE FROM projeto")

        cur.execute("SELECT produtor.nome_produtor AS produtor, entidade.nome_entidade AS entidade, produto.nome_produto AS produto, ST_Distance_Sphere(produtor.geom_produtor, entidade.geom_entidade)/1000 AS distancia, (preco_produto*quant_demandado) AS valor_demandado,(preco_produto*quant_demandado) / prodcont.conta AS valor_produzido,CAST(quant_demandado / prodcont.conta AS float) AS quant_produzido,entidade2.valor_produzido * preco_produto / produto2.num_produto AS valor_produzido_total,CAST(produtor2.num_produtor AS int) AS produto_por_produtor,CAST(produto2.num_produto AS int) AS total_produtor_por_produto,CAST(prodcont.conta AS int) AS produtor_por_produto,(SELECT CASE WHEN data_inicio_produzido > data_inicio_demandado THEN data_inicio_produzido WHEN data_inicio_produzido < data_inicio_demandado THEN data_inicio_demandado ELSE data_inicio_demandado END) AS data_inicio, (SELECT CASE WHEN data_fim_produzido < data_fim_demandado THEN data_fim_produzido WHEN data_fim_produzido > data_fim_demandado THEN data_fim_demandado ELSE data_fim_demandado END) AS data_fim, ST_MakeLine(produtor.geom_produtor, entidade.geom_entidade) FROM produtor, entidade, produto, produto_produzido, produto_demandado INNER JOIN(SELECT produto.nome_produto AS produto, SUM(quant_demandado) AS valor_produzido FROM entidade, produto_demandado, produto WHERE entidade.id_entidade = produto_demandado.id_entidade AND produto.id_produto = produto_demandado.id_produto GROUP BY produto.nome_produto) AS entidade2 ON produto = entidade2.produto INNER JOIN(SELECT produtor.nome_produtor AS produtor, SUM(CAST(produto_produzido.tipo_produzido AS int)) AS num_produtor FROM produtor, produto_produzido, produto WHERE produtor.id_produtor = produto_produzido.id_produtor AND produto.id_produto = produto_produzido.id_produto GROUP BY produtor.id_produtor) AS produtor2 ON produtor = produtor2.produtor INNER JOIN(SELECT produto.nome_produto AS produto1, SUM(CAST(produto_produzido.tipo_produzido AS int)) AS num_produto FROM produtor, produto_produzido, produto WHERE produtor.id_produtor = produto_produzido.id_produtor AND produto.id_produto = produto_produzido.id_produto GROUP BY produto.nome_produto) AS produto2 ON produto = produto2.produto1 INNER JOIN(SELECT nome_produto AS prodcont1, nome_entidade AS entidade, COUNT(produtor.nome_produtor) AS conta FROM produtor, entidade, produto, produto_produzido WHERE produtor.id_produtor = produto_produzido.id_produtor AND produto.id_produto = produto_produzido.id_produto AND ST_Distance_Sphere(entidade.geom_entidade, produtor.geom_produtor) < produto.distancia_produto AND produto_produzido.tipo_produzido = 'true' GROUP BY nome_produto, nome_entidade) AS prodcont ON produto = prodcont.prodcont1 WHERE produtor.id_produtor = produto_produzido.id_produtor AND entidade.id_entidade = produto_demandado.id_entidade AND produto.id_produto = produto_produzido.id_produto AND produto.id_produto = produto_demandado.id_produto AND produto.nome_produto = entidade2.produto AND produtor.nome_produtor = produtor2.produtor AND produto.nome_produto = produto2.produto1 AND produto.nome_produto = prodcont.prodcont1 AND entidade.nome_entidade = prodcont.entidade AND produto_demandado.quant_demandado > 0 AND produto_produzido.tipo_produzido = 'true' AND ST_Distance_Sphere(produtor.geom_produtor, entidade.geom_entidade) < 100000 AND(data_inicio_produzido, data_fim_produzido) OVERLAPS (data_inicio_demandado, data_fim_demandado) = 'true' ORDER BY produtor, entidade, produto")

        self.dlg.prod_enti_prod_tableWidget.setColumnCount(8)
        self.dlg.prod_enti_prod_tableWidget.setHorizontalHeaderLabels(['Produtor', 'Entidade', 'Produto', 'Distancia', 'Valor', 'Quantidade', 'Data de Inicio', 'Data de Fim'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.prod_enti_prod_tableWidget.insertRow(row)
            nome_produtor = QTableWidgetItem(str(nome[0]))
            nome_entidade = QTableWidgetItem(str(nome[1]))
            nome_produto = QTableWidgetItem(str(nome[2]))
            distancia = QTableWidgetItem(str(nome[3]))
            valor = QTableWidgetItem(str(nome[5]))
            quantidade = QTableWidgetItem(str(nome[6]))
            data_inicio = QTableWidgetItem(str(nome[11]))
            data_fim = QTableWidgetItem(str(nome[12]))
            self.dlg.prod_enti_prod_tableWidget.setItem(row, 0, nome_produtor)
            self.dlg.prod_enti_prod_tableWidget.setItem(row, 1, nome_entidade)
            self.dlg.prod_enti_prod_tableWidget.setItem(row, 2, nome_produto)
            self.dlg.prod_enti_prod_tableWidget.setItem(row, 3, distancia)
            self.dlg.prod_enti_prod_tableWidget.setItem(row, 4, valor)
            self.dlg.prod_enti_prod_tableWidget.setItem(row, 5, quantidade)
            self.dlg.prod_enti_prod_tableWidget.setItem(row, 6, data_inicio)
            self.dlg.prod_enti_prod_tableWidget.setItem(row, 7, data_fim)
            row = row + 1


#-------

            cur.execute("INSERT INTO projeto (nome_produtor, nome_entidade, nome_produto, distancia, valor_produzido, quant_produzido, data_inicio, data_fim, geom_projeto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", [nome[0], nome[1], nome[2], nome[3], nome[5], nome[6], nome[11], nome[12], nome[13]])

#-------



        cur.execute("DELETE FROM fluxo_prod_enti")

        cur.execute("SELECT projeto.nome_produtor AS produtor, projeto.nome_entidade AS entidade, SUM(projeto.valor_produzido) AS soma_valor_produzido, SUM(projeto.quant_produzido) AS soma_quant_produzido, ST_MakeLine(produtor.geom_produtor, entidade.geom_entidade) FROM projeto, produtor, entidade WHERE projeto.nome_produtor = produtor.nome_produtor AND projeto.nome_entidade = entidade.nome_entidade GROUP BY projeto.nome_produtor, projeto.nome_entidade, produtor.geom_produtor, entidade.geom_entidade ORDER BY projeto.nome_produtor")

        self.dlg.prod_enti_tableWidget.setColumnCount(4)
        self.dlg.prod_enti_tableWidget.setHorizontalHeaderLabels(['Produtor', 'Entidade', 'Valor', 'Quantidade'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.prod_enti_tableWidget.insertRow(row)
            nome_produtor = QTableWidgetItem(str(nome[0]))
            nome_entidade = QTableWidgetItem(str(nome[1]))
            valor = QTableWidgetItem(str(nome[2]))
            quantidade = QTableWidgetItem(str(nome[3]))
            self.dlg.prod_enti_tableWidget.setItem(row, 0, nome_produtor)
            self.dlg.prod_enti_tableWidget.setItem(row, 1, nome_entidade)
            self.dlg.prod_enti_tableWidget.setItem(row, 2, valor)
            self.dlg.prod_enti_tableWidget.setItem(row, 3, quantidade)
            row = row + 1

            cur.execute("INSERT INTO fluxo_prod_enti (nome_produtor, nome_entidade, soma_valor_produzido, soma_quant_produzido, geom_fluxo_prod_ent) VALUES (%s, %s, %s, %s, %s);", [nome[0], nome[1], nome[2], nome[3], nome[4]])



        cur.execute("DELETE FROM fluxo_cent_enti")

        cur.execute("SELECT nome_central AS central, projeto.nome_entidade AS entidade, SUM(projeto.valor_produzido) AS soma_valor_produzido, SUM(projeto.quant_produzido) AS soma_quant_produzido, ST_MakeLine(central.geom_central, entidade.geom_entidade) FROM projeto, produtor, central, entidade WHERE projeto.nome_produtor = produtor.nome_produtor AND produtor.id_central = central.id_central AND projeto.nome_entidade = entidade.nome_entidade GROUP BY nome_central, projeto.nome_entidade, central.geom_central, entidade.geom_entidade ORDER BY nome_central")

        self.dlg.cent_enti_tableWidget.setColumnCount(4)
        self.dlg.cent_enti_tableWidget.setHorizontalHeaderLabels(['Central', 'Entidade', 'Valor', 'Quantidade'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.cent_enti_tableWidget.insertRow(row)
            nome_central = QTableWidgetItem(str(nome[0]))
            nome_entidade = QTableWidgetItem(str(nome[1]))
            valor = QTableWidgetItem(str(nome[2]))
            quantidade = QTableWidgetItem(str(nome[3]))
            self.dlg.cent_enti_tableWidget.setItem(row, 0, nome_central)
            self.dlg.cent_enti_tableWidget.setItem(row, 1, nome_entidade)
            self.dlg.cent_enti_tableWidget.setItem(row, 2, valor)
            self.dlg.cent_enti_tableWidget.setItem(row, 3, quantidade)
            row = row + 1

            cur.execute("INSERT INTO fluxo_cent_enti (nome_central, nome_entidade, soma_valor_produzido, soma_quant_produzido, geom_fluxo_cent_ent) VALUES (%s, %s, %s, %s, %s);", [nome[0], nome[1], nome[2], nome[3], nome[4]])







        cur.execute("SELECT nome_produtor AS produtor, nome_produto AS produto, SUM(projeto.valor_produzido) AS soma_valor_produzido, SUM(projeto.quant_produzido) AS soma_quant_produzido FROM projeto GROUP BY nome_produtor, nome_produto ORDER BY nome_produtor")

        self.dlg.prod_prod_tableWidget.setColumnCount(4)
        self.dlg.prod_prod_tableWidget.setHorizontalHeaderLabels(['Produtor', 'Produto', 'Valor', 'Quantidade'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.prod_prod_tableWidget.insertRow(row)
            nome_produtor = QTableWidgetItem(str(nome[0]))
            nome_produto = QTableWidgetItem(str(nome[1]))
            valor = QTableWidgetItem(str(nome[2]))
            quantidade = QTableWidgetItem(str(nome[3]))
            self.dlg.prod_prod_tableWidget.setItem(row, 0, nome_produtor)
            self.dlg.prod_prod_tableWidget.setItem(row, 1, nome_produto)
            self.dlg.prod_prod_tableWidget.setItem(row, 2, valor)
            self.dlg.prod_prod_tableWidget.setItem(row, 3, quantidade)
            row = row + 1



        cur.execute("DELETE FROM produtor_final")

        cur.execute("SELECT projeto.nome_produtor AS produtor, SUM(projeto.valor_produzido) AS soma_valor_produzido,  SUM(projeto.quant_produzido) AS soma_quant_produzido, produtor.geom_produtor FROM projeto, produtor WHERE projeto.nome_produtor = produtor.nome_produtor GROUP BY projeto.nome_produtor, produtor.geom_produtor ORDER BY projeto.nome_produtor")

        row = 0
        for nome in cur.fetchall():
            cur.execute("INSERT INTO produtor_final (nome_produtor, soma_valor_produzido, soma_quant_produzido, geom_produtor_final) VALUES (%s, %s, %s, %s);", [nome[0], nome[1], nome[2], nome[3]])




        cur.execute("SELECT nome_entidade AS entidade, nome_produto AS produto, SUM(projeto.valor_produzido) AS soma_valor_produzido, SUM(projeto.quant_produzido) AS soma_quant_produzido FROM projeto GROUP BY nome_entidade, nome_produto ORDER BY nome_entidade")

        self.dlg.produ_enti_tableWidget.setColumnCount(4)
        self.dlg.produ_enti_tableWidget.setHorizontalHeaderLabels(['Entidade', 'Produto', 'Valor', 'Quantidade'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.produ_enti_tableWidget.insertRow(row)
            nome_entidade = QTableWidgetItem(str(nome[0]))
            nome_produto = QTableWidgetItem(str(nome[1]))
            valor = QTableWidgetItem(str(nome[2]))
            quantidade = QTableWidgetItem(str(nome[3]))
            self.dlg.produ_enti_tableWidget.setItem(row, 0, nome_entidade)
            self.dlg.produ_enti_tableWidget.setItem(row, 1, nome_produto)
            self.dlg.produ_enti_tableWidget.setItem(row, 2, valor)
            self.dlg.produ_enti_tableWidget.setItem(row, 3, quantidade)
            row = row + 1




        cur.execute("DELETE FROM entidade_final")

        cur.execute("SELECT projeto.nome_entidade AS entidade, SUM(projeto.valor_produzido) AS soma_valor_produzido, SUM(projeto.quant_produzido) AS soma_quant_produzido, entidade.geom_entidade FROM projeto, entidade WHERE projeto.nome_entidade = entidade.nome_entidade GROUP BY projeto.nome_entidade, entidade.geom_entidade ORDER BY projeto.nome_entidade")

        row = 0
        for nome in cur.fetchall():
            cur.execute("INSERT INTO entidade_final (nome_entidade, soma_valor_produzido, soma_quant_produzido, geom_entidade_final) VALUES (%s, %s, %s, %s);", [nome[0], nome[1], nome[2], nome[3]])




        cur.execute("SELECT nome_central AS central, nome_produto AS produto, SUM(projeto.valor_produzido) AS soma_valor_produzido, SUM(projeto.quant_produzido) AS soma_quant_produzido FROM projeto, produtor, central WHERE projeto.nome_produtor = produtor.nome_produtor AND central.id_central = produtor.id_central GROUP BY nome_central, nome_produto ORDER BY nome_central")

        self.dlg.cent_enti_tableWidget.setColumnCount(4)
        self.dlg.cent_enti_tableWidget.setHorizontalHeaderLabels(['Central', 'Produto', 'Valor', 'Quantidade'])
        row = 0
        for nome in cur.fetchall():
            self.dlg.prod_cent_tableWidget.insertRow(row)
            nome_central = QTableWidgetItem(str(nome[0]))
            nome_produto = QTableWidgetItem(str(nome[1]))
            valor = QTableWidgetItem(str(nome[2]))
            quantidade = QTableWidgetItem(str(nome[3]))
            self.dlg.prod_cent_tableWidget.setItem(row, 0, nome_central)
            self.dlg.prod_cent_tableWidget.setItem(row, 1, nome_produto)
            self.dlg.prod_cent_tableWidget.setItem(row, 2, valor)
            self.dlg.prod_cent_tableWidget.setItem(row, 3, quantidade)
            row = row + 1




        cur.execute("DELETE FROM central_final")

        cur.execute("SELECT nome_central AS central, SUM(projeto.valor_produzido) AS soma_valor_produzido, SUM(projeto.quant_produzido) AS soma_quant_produzido, geom_central FROM projeto, produtor, central WHERE projeto.nome_produtor = produtor.nome_produtor AND central.id_central = produtor.id_central GROUP BY nome_central, geom_central ORDER BY nome_central")

        row = 0
        for nome in cur.fetchall():
            cur.execute("INSERT INTO central_final (nome_central, soma_valor_produzido, soma_quant_produzido, geom_central_final) VALUES (%s, %s, %s, %s);", [nome[0], nome[1], nome[2], nome[3]])





        # Desconectar do banco de dados
        conn.commit()
        cur.close()
        conn.close()
