import { useState } from 'react'
import './App.css'
import React from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';


function App() {

  pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

  var dataPdf;
  const [sourcePDF, setSourcePDF] = useState(dataPdf)
  const [textAreaRows, setRows] = useState(1)
  const [zipDisable, setZipDisable] = useState(true)
  const [uploadBtnDisabled, setUploadBtnDisabled] = useState(false)
  const [user, setUser] = useState("none")

  const [selectedImage, setSelectedImage] = useState(null)

  function onClickRender() {
    setIsDisabled(true)
    const texText = document.getElementById('TexFrame')
    var text = texText.value
    console.log(text)
    const KeyOptions = {
      method: 'POST',
      headers:{
        'Content-type': 'application/json'
      },
      body: JSON.stringify({
        tex: text
      }),
    };
    fetch(`http://188.44.41.132:8000/renderTex/${user}`, KeyOptions)
    .then(response => {
      if (response.ok) {
        const error = document.getElementById('statusError');
        error.textContent = "";
        error.classList.remove("errorMsg")
        return response.blob()
      } else {
        throw new Error('');
      }
    })
    .then(data => {
      setSourcePDF(data)
    }).catch(err => {
      const error = document.getElementById('statusError');
      error.textContent = "Cannot render this tex file or files has been deleted (files stores only for 30 minutes)"
      error.classList.add("errorMsg")
      error.classList.remove("msg")
    })
  }

  function onDownloadBtn() {
    console.log(user)
    const options = {
      method: 'GET',
    };
    fetch(`http://188.44.41.132:8000/zip/${user}`, options)
    .then(response => response.blob())
    .then(data => {
      const download = document.createElement('a')
      download.href = URL.createObjectURL(data)
      download.download = "files.zip"
      download.click()
    })
  }

  function onUploadBtnClicked(element) {
    document.getElementById("uploadBtn").classList.add("spinning")
    document.getElementById("TexFrame").value = "";
    setUploadBtnDisabled(true)
    setZipDisable(true)
    setSourcePDF(null)
    const error = document.getElementById('statusError');
    error.textContent = "Подождите немного ваше изображение / документ обрабатывается"
    error.classList.remove("errorMsg")
    error.classList.add("msg")
    console.log("something")
    const fileInput = document.querySelector('input[type="file"]') ;
    const formData = new FormData();
    if (fileInput.files[0] == null) {
      error.classList.add("errorMsg")
      error.classList.remove("msg")
      error.textContent = "Выберите файл перед отправкой на обработку"
      setUploadBtnDisabled(false)
      console.log(element.target.getAttribute("disabled"))
      element.target.classList.remove("spinning")
      return;
    }
    formData.append('file', fileInput.files[0]);
    const KeyOptions = {
      method: 'POST',
      body: formData,
    };
    
    console.log("fetching")
    fetch('http://188.44.41.132:8000/uploadFile', KeyOptions)
    .then(async responce => {
      if (responce.status != 200) {
        var text = await responce.json()
        console.log(text)
        error.textContent = text.detail
        error.classList.add("errorMsg")
        error.classList.remove("msg")
        throw new Error('')
      }
      return await responce.text()
    }).then(data => {
      const options = {
        method: 'GET',
        
      };
      console.log(data)
      data = data.substring(1, data.length - 1)
      setUser(data);
      console.log(typeof user)
      console.log(typeof data)
      setZipDisable(false)
      setUploadBtnDisabled(false)
      element.target.classList.remove("spinning")
        fetch(`http://188.44.41.132:8000/tex/${data}/`, options)
        .then(response => {
          if (response.ok)
            return response.text()
          else
            throw new Error('');
        })
        .then(data => {
          data = data.substring(1, data.length - 1);
          let str = data;
          
          console.log(str);
          str = str.split("\\n").join("\r\n")
          str = str.split("\\\\").join("\\");
          str = str.split("\noindent").join("\\noindent")
          console.log(str);

          const TexPage = document.getElementById("TexFrame");
          TexPage.value = str;
          setRows(str.split('\n').length)
          document.getElementById("latex").click()
        }).catch(err => {
          const error = document.getElementById('statusError');
          error.textContent = "Try1111 to upload file again (all files stores only 30 minutes)"
          error.classList.add("errorMsg")
          error.classList.remove("msg")
        })


        fetch(`http://188.44.41.132:8000/pdf/${data}/`, options)
        .then(response => {
          if (response.ok)
            return response.blob()
          else
            throw new Error('');
        })
        .then(data=> {
          dataPdf = data;
          setSourcePDF(URL.createObjectURL(dataPdf))
          console.log(dataPdf)
          error.textContent = ""
        }).catch(err => {
          const error = document.getElementById('statusError');
          error.textContent = "Мы не смогли получить сгенерированый pdf из latex возможно у нас ошибка в распознавании"
          error.classList.add("errorMsg")
          error.classList.remove("msg")
        })
    }).catch(err => {
      console.log(err)
      element.target.classList.remove("spinning")
      setUploadBtnDisabled(false)
    })
    
  }

  

  // Функция для переключения между вкладками
  function switchTab(tabName) {
    const name = tabName.target.getAttribute("id") + "Tab"
    // Скрыть все вкладки
    const tabContents = document.getElementsByClassName('tabContent');
    for (let tabContent of tabContents) {
        tabContent.style.display = 'none';
    }

    // Убрать активный класс у всех кнопок
    const tabButtons = document.getElementsByClassName('tabButton');
    for (let tabButton of tabButtons) {
      tabButton.classList.remove('active');
    }

    // Отобразить выбранную вкладку
    document.getElementById(name).setAttribute('style', 'display: block')
    document.getElementById(tabName.target.getAttribute("id")).classList.add('active')
   }


  function onChangeTextArea(element) {
    setRows((element.target ? element.target.value.split("\n").length : 0) + 2)
  }


  function onChangeImageSelected(element) {
    document.getElementById("statusError").textContent = ""
    if (element.target.files[0] != null) {
      const upload = URL.createObjectURL(element.target.files[0]);
      setSelectedImage(upload);
      document.getElementById("uploaded").click()
    }
  }

  return (
    <>
      <div className="container">
        <h1>Image2LaTeX</h1>
        
        {/* <!-- Форма для загрузки документа или фотографии --> */}
        <div id="uploadForm">
            <input type="file" id="fileInput" onChange={onChangeImageSelected} name="fileInput" accept="image/*, .pdf" required></input>
            <button id="uploadBtn" onClick={onUploadBtnClicked} disabled={uploadBtnDisabled}>Загрузить документ или фотографию</button>
            <button onClick={onDownloadBtn} disabled={zipDisable}>Скачать zip</button>
        </div>

        <div id="statusError">
        </div>

        {/* <!-- Вкладки для переключения между представлениями --> */}
        <div className="tabs">
            <button className="tabButton" id="uploaded" onClick={switchTab}>Загруженное изображение/документ</button>
            <button className="tabButton" id="latex" onClick={switchTab}>LaTeX код</button>
            <button className="tabButton" id="pdf" onClick={switchTab}>PDF документ</button>
        </div>

        {/* <!-- Отображение загруженной фотографии или документа --> */}
        <div id="uploadedTab" className="tabContent" style={{display: 'none'}}>
            <h2>Загруженное изображение или документ:</h2>
            <embed id="uploadedImage" src={selectedImage} alt="Загруженное изображение или документ"></embed>
        </div>

        {/* <!-- Отображение LaTeX кода --> */}
        <div id="latexTab" className="tabContent" style={{display: 'none'}}>
            <h2>LaTeX код:</h2>
            <pre id="latexCode"></pre>
            <textarea rows={textAreaRows} id="TexFrame" onChange={onChangeTextArea}></textarea >
        </div>

        {/* <!-- Отображение PDF документа --> */}
        <div id="pdfTab" className="tabContent" style={{display: 'none'}}>
            <h2>PDF документ:</h2>
            <div id="pdfContainer">
                <embed id="pdfViewer" src={sourcePDF} type="application/pdf" width="100%" height="600px"></embed>
            </div>
        </div>
    </div>
    </>
  )
}

export default App


      // <div className="App">
      //   <div className="App-header">
      //     <div className="MainAppBlock">

      //       <div className="SpecialButtons">
      //         <div>
      //           <button id="showOrigin" type="button" disabled={isPreview} onClick={onClickPreview}>show origin</button>
      //         </div>
      //         <div>
      //           <button hidden={true}></button>
      //         </div>
      //       </div>

      //       <div className="TextBlock" id="texBlock">

      //         <div className="FilesPreview" hidden={!showOrigin}>
      //           <div className="documentView">
      //             <img id="imgOrigin" src="" alt="not found" />
      //           </div>
      //         </div>

      //         <div className="FilesPreview" hidden={showOrigin}>
      //           <div className='texView'>
      //             <textarea id="TexFrame" onChange={onChangeTex}>
      //             </textarea >
      //           </div>
      //         </div>

      //         <div className="FilesPreview" id="texVis">
      //           <div className='documentView'>
      //             <Document file={sourcePDF} onLoadSuccess={onDocumentLoadSuccess}>
      //               <Page pageNumber={pageNumber}>

      //               </Page>
      //             </Document>
      //           </div>
      //         </div>

      //       </div>

      //       <div className="SpecialButtons">
      //         <div>
      //           <button type="button" disabled={idDisabled} onClick={onClickRender}>render</button>
      //           <div id='statusError'></div>
      //         </div>
      //       <div>
      //         <button
      //           type="button"
      //           disabled={pageNumber <= 1}
      //           onClick={previousPage}>
      //           Previous
      //         </button>
      //         <button
      //           type="button"
      //           disabled={pageNumber >= totalPages}
      //           onClick={nextPage}>
      //           Next
      //         </button>
      //         </div>
      //       </div>

      //       <div className="BtnBlock">
      //         <div>
      //             <input type="file" className="DownloadBtn" id="uploadFile"></input>
      //         </div>
      //         <div className="SpecialButtons">
      //           <button className="LoadBtn" id="myButton" onClick={onUploadBtnClicked}>Upload File</button>
      //           <div>
      //             <div hidden={uploadHidden}>
      //               <span className="loader"></span>
      //             </div>
      //           </div>
      //         </div>
      //         <div className="SpecialButtons">
      //           <a id="download">
      //             <button className="LoadBtn" onClick={onDownloadBtn}> Download LaTex</button>
      //           </a>
      //           <div>
      //             <div hidden={downloadHidden}>
      //               <span className="loader"></span>
      //             </div>
      //           </div>
      //         </div>
                
      //       </div>  

      //     </div>
          
      //   </div>
      // </div>