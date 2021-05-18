$(document).ready(function(){
    const csrftoken = getCookie('csrftoken');
    $('#tip').popover({
        container: 'body',
        animation : true,
        html : true,
        trigger: 'focus',
        title : `Tip การจัดการแบบสอบถาม`,
        template : `<div class="popover" role="tooltip">
            <div class="arrow"></div>
            <h3 class="popover-header bg-warning" ></h3>
            <div class="popover-body"></div>
        </div>`,
        content: `<ul>
        <li>สมาชิกสามารถสร้างแบบสอบถามได้</li>
        <li>สมาชิกสามารถแก้ไขแบบสอบถามได้</li>
        <li>แบบสอบถามที่ไม่มีการ Vote สามารถลบได้</li>
        <li>แบบสอบถามที่มีการ Vote ให้คะแนนแล้วจะไม่สามารถลบได้ แต่ปิดการใช้งานได้</li>
        <li>สมาชิกไม่สามารถ Vote ได้มากกว่า 1 ครั้ง</li>
    </ul>`
    })
    
    $('.confirm-delete').click(function(){
        let id = $(this).find("i").first().attr("data-id")
        let title = $(this).find("i").first().attr("data-title")
        Swal.fire({
            title: "ยืนยันการลบแบบสอบถาม",
            text : `คุณต้องการลบแบบสอบถาม : ${title} ? `,
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
                        html : `<i class='fas fa-poll' style='color: #dc3545;'></i> ${title}`,
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
})
