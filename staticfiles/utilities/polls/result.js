$(document).ready(function(){
    const csrftoken = getCookie('csrftoken');


    $('.confirm-delete').click(function(e){
        e.preventDefault()
        Swal.fire({
            title: "ยืนยันการลบแบบสอบถาม",
            text : `คุณต้องการลบแบบสอบถาม : ${name} ? `,
            icon : 'warning',
            showCancelButton : true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#ffc107',
            confirmButtonText: '<i class="fas fa-check"></i> ยืนยัน',
            cancelButtonText: '<i class="fas fa-times"></i> ยกเลิก',
        }).then((result) =>{
            if(result.isConfirmed){
                try {
                    Swal.fire({
                        title : '<i class="fas fa-spinner fa-spin" style="color: #dc3545;"></i> กำลังลบแบบสอบถาม',
                        html : `<i class='fas fa-poll' style='color: #dc3545;'></i> ${name}`,
                        showConfirmButton : false,
                        allowOutsideClick : false,
                        allowEscapeKey : false,
                        allowEnterKey : false,
                    })
                    var request = $.ajax({
                        url : url_detail.replace("99999",id),
                        headers: {'X-CSRFToken': csrftoken},
                        method: "DELETE",
                        contentType: 'application/json; charset=UTF-8',
                        dataType: 'json',
                    })
                    request.done((res,textStatus,jqXHR)=>{
                        try {
                            Swal.close()
                            Swal.fire({
                                title: 'Success!',
                                text: `ลบข้อมูลแบบสอบถามและตัวเลือกสำเร็จ.` ,
                                icon: 'success'
                            }).then(()=>{
                                window.location.assign(url_own)
                            })
                        } catch (error) {
                            Swal.close()
                            Swal.fire({
                                title: `error : ${error}`,
                                text : `กรุณาติดต่อผู้ดูแลระบบ เมนูติดต่อเรา`,
                                icon : 'error'
                            })
                        }
                    })
                    request.fail((jqXHR, textStatus, errorThrown)=>{
                        //console.log("Request failed: " + textStatus)
                        //console.log(jqXHR)
                        if(jqXHR.status == 403 || jqXHR.status == 401) gotoLogout()
                        Swal.fire({
                            title : `${textStatus} ${jqXHR.status} : ${errorThrown}`,
                            text: jqXHR.responseJSON ? jqXHR.responseJSON.error : ``,
                            icon : 'error'
                        })
                    })
                } catch (error) {
                    Swal.close()
                    Swal.fire({
                        title: `error : ${error}`,
                        text : `กรุณาติดต่อผู้ดูแลระบบ เมนูติดต่อเรา`,
                        icon : 'error'
                    })
                }
            }
            // else console.log("cancel!")
            else return false
        })
    })


    $(".confirm-disable").click(function(e){
        e.preventDefault()
        const title = $('.confirm-disable-text').text()
        Swal.fire({
            title: `ยืนยัน${title}`,
            text : `คุณต้องการ${title} ? `,
            icon : 'warning',
            showCancelButton : true,
            confirmButtonColor: '#28a745',
            cancelButtonColor: '#dc3545',
            confirmButtonText: '<i class="fas fa-check"></i> ยืนยัน',
            cancelButtonText: '<i class="fas fa-times"></i> ยกเลิก',
        }).then((result)=>{
            if(result.isConfirmed){
                try {
                    Swal.fire({
                        title : '<i class="fas fa-spinner fa-spin" style="color: #dc3545;"></i> กำลังปรับปรุงสถานะแบบสอบถาม',
                        html : `<i class='fas fa-poll' style='color: #dc3545;'></i> ${name}`,
                        showConfirmButton : false,
                        allowOutsideClick : false,
                        allowEscapeKey : false,
                        allowEnterKey : false,
                    })

                    new Promise(function(resolve,reject){
                        const request = $.ajax({
                            url : url_api_detail.replace("99999",id),
                            headers: {'X-CSRFToken': csrftoken},
                            method: "GET",
                            contentType: 'application/json; charset=UTF-8',
                            dataType: 'json',
                        })
                        request.done((res,textStatus,jqXHR)=>{
                            try {
                                resolve(res)
                            } catch (error) {
                                Swal.close()
                                Swal.fire({
                                    title: `error : ${error}`,
                                    text : `กรุณาติดต่อผู้ดูแลระบบ เมนูติดต่อเรา`,
                                    icon : 'error'
                                })
                            }
                        })
                        request.fail((jqXHR, textStatus, errorThrown)=>{
                            //console.log("Request failed: " + textStatus)
                            //console.log(jqXHR)
                            if(jqXHR.status == 403 || jqXHR.status == 401) gotoLogout()
                            Swal.fire({
                                title : `${textStatus} ${jqXHR.status} : ${errorThrown}`,
                                text: jqXHR.responseJSON ? jqXHR.responseJSON.error : ``,
                                icon : 'error'
                            })
                        })
                    }).then(function(result){
                        console.log(!result.closed)
                        const request = $.ajax({
                            url : url_api_detail.replace("99999",id),
                            headers: {'X-CSRFToken': csrftoken},
                            method: "PATCH",
                            contentType: 'application/json; charset=UTF-8',
                            dataType: 'json',
                            data : JSON.stringify({
                                'closed' : !result.closed
                            })
                        })
                        request.done((res,textStatus,jqXHR)=>{
                            try {
                                Swal.close()
                                Swal.fire({
                                    title: 'Success!',
                                    text: `ปรับปรุงสถานะแบบสอบถามสำเร็จ.` ,
                                    icon: 'success'
                                }).then(()=>{
                                    window.location.assign(url_result.replace("99999",id))
                                })
                            } catch (error) {
                                Swal.close()
                                Swal.fire({
                                    title: `error : ${error}`,
                                    text : `กรุณาติดต่อผู้ดูแลระบบ เมนูติดต่อเรา`,
                                    icon : 'error'
                                })
                            }
                        })
                    })
                } catch (error) {
                    Swal.close()
                    Swal.fire({
                        title: `error : ${error}`,
                        text : `กรุณาติดต่อผู้ดูแลระบบ เมนูติดต่อเรา`,
                        icon : 'error'
                    })
                }
            }
        })
        
    })
    
})