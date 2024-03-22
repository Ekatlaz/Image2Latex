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
  const [user, setUser] = useState("");

  const [idDisabled, setIsDisabled] = useState(true)
  const [totalPages, setTotalPages] = useState(1);
  const [pageNumber, setPageNumber] = useState(1);

  const onChangeTex =() => {
    console.log("asdfasdfasdfasdfasdfasdf")
    setIsDisabled(false)
  }
 
  const onDocumentLoadSuccess = ({ numPages }) => {
    setTotalPages(numPages);
  }
 
  const previousPage = () => {
    setPageNumber(prevPageNumber => prevPageNumber - 1);
  }
 
  const nextPage = () => {
    setPageNumber(prevPageNumber => prevPageNumber + 1);
  }

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
    fetch(`http://localhost:8000/renderTex/${user}`, KeyOptions)
    .then(response => {
      if (response.ok) {
        const error = document.getElementById('statusError');
        error.textContent = "";
        return response.blob()
      } else {
        throw new Error('');
      }
    })
    .then(data => {
      setSourcePDF(data)
    }).catch(err => {
      const error = document.getElementById('statusError');
      error.textContent = "Cannot render this tex file"
    })
  }

  function onUploadBtnClicked() {
    console.log("something")
    const fileInput = document.querySelector('input[type="file"]') ;
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    const KeyOptions = {
      method: 'POST',
      body: formData,
    };
    
    console.log("fetching")
    fetch('http://localhost:8000/uploadFile', KeyOptions)
    .then(responce => responce.text())
    .then(data => {
      const options = {
        method: 'GET',
        
      };
    console.log(data)
    data = data.substring(1,data.length-1)
    setUser(data)
    console.log(user);
      fetch(`http://localhost:8000/tex/${data}/`, options)
      .then(responce => responce.text())
      .then(data => {
        data = data.substring(1, data.length - 1);
        let str = data;
        str = str.split("\\n").join("\r\n")
        str = str.split("\\\\").join("\\");
        console.log(str);

        const TexPage = document.getElementById("TexFrame");
        TexPage.value = str;
        setEdit(true)
      })


      fetch(`http://localhost:8000/pdf/${data}/`, options)
      .then(response => response.blob())
      .then(data=> {
        dataPdf = data;
        setSourcePDF(dataPdf)
        console.log(dataPdf)
      })

      fetch(`http://localhost:8000/zip/${data}/`, options)
      .then(response => response.blob())
      .then(data => {
        const download = document.getElementById('download')
        download.href = URL.createObjectURL(data)
        download.download = "files.zip"
      })
    })
  }

  return (
    <>
      <div className="App">
      <div className="App-header">
        <div className="MainAppBlock">
          <div className="TextBlock" id="texBlock">
            <div className="FilesPreview">
              <div className='texView'>
                <textarea id="TexFrame" onChange={onChangeTex}>
                </textarea >
              </div>
            </div>
            <div className="FilesPreview" id="texVis">
              <div className='documentView'>
                <Document file={sourcePDF} onLoadSuccess={onDocumentLoadSuccess}>
                  <Page pageNumber={pageNumber}>

                  </Page>
                </Document>
              </div>
            </div>
          </div>
          <div className="SpecialButtons">
            <div>
              <button type="button" disabled={idDisabled} onClick={onClickRender}>render</button>
              <div id='statusError'></div>
            </div>
           <div>
            <button
              type="button"
              disabled={pageNumber <= 1}
              onClick={previousPage}>
              Previous
            </button>
            <button
              type="button"
              disabled={pageNumber >= totalPages}
              onClick={nextPage}>
              Next
            </button>
            </div>
          </div>
          <div className="BtnBlock">
            <div>
                <input type="file" className="DownloadBtn" id="uploadFile"></input>
            </div>
            <div>
              <button className="LoadBtn" id="myButton" onClick={onUploadBtnClicked}> Upload File</button>
            </div>
              <a id="download">
                <button className="LoadBtn" > Download LaTex</button>
              </a>
              
          </div>  
        </div>
        
      </div>
    </div>
    </>
  )
}

export default App
