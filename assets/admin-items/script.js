class ItemHandler {
    selectedItems = [];

    constructor() {
        const self = this;
        $(function () {
            self.moneyUnit = $(".index-sales__view-tbody").data("moneyunit");
            self.getActive();
            self.listener();
            self.selectButtons();
        });
    }

    applyButton() {
        const self = this;
        self.selectedItems = [];
        $(".index-sales__button:checked").each(function (index, element) {
            self.selectedItems.push($(element).val());
        });

        const itemLength = self.selectedItems.length;
        if (itemLength === 0) {
            $("#endSale").prop("disabled", true);
            $("#setSale").prop("disabled", true);
            $("#edit").prop("disabled", true);
            $("#stop").prop("disabled", true);
        } else if (itemLength === 1) {
            $("#endSale").prop("disabled", false);
            $("#setSale").prop("disabled", false);
            $("#edit").prop("disabled", false);
            $("#stop").prop("disabled", false);
        } else {
            $("#endSale").prop("disabled", false);
            $("#setSale").prop("disabled", false);
            $("#edit").prop("disabled", true);
            $("#stop").prop("disabled", true);
        }
    }

    listener() {
        const self = this;

        /** セール設定 **/
        $("#setSale").click(function () {
            $("#discountRate").val(null);
            $("#startDate").val(null);
            $("#endDate").val(null);
            $("#prideOnly").prop("checked", false)

            $(".index-sales__view").css("display", "none");
            $(".index-sales__sale1").css("display", "block");
        });

        $("#setSalePrev1").click(function () {
            $(".index-sales__sale1").css("display", "none");
            $(".index-sales__view").css("display", "block");
        });

        $("#setSaleNext").click(function () {
            const discountRate = $("#discountRate").val();
            const startDate = $("#startDate").val();
            const endDate = $("#endDate").val();
            const prideOnly = $("#prideOnly option:selected").val();

            $(".outOfRange").css("display", "none");
            $(".requiredItem1").css("display", "none");
            $(".requiredItem2").css("display", "none");
            $(".requiredItem3").css("display", "none");

            let error = false;
            if (!discountRate) {
                $(".requiredItem1").css("display", "block");
                error = true
            } else if (Number(discountRate) < 1 || 100 < Number(discountRate)) {
                $(".outOfRange").css("display", "block");
                error = true
            }
            if (!startDate) {
                $(".requiredItem2").css("display", "block");
                error = true
            }
            if (!endDate) {
                $(".requiredItem3").css("display", "block");
                error = true
            }

            if (error) return;

            $("#confirm_discountRate").text(discountRate);
            $("#confirm_startDate").text(startDate);
            $("#confirm_endDate").text(endDate);
            $("#confirm_prideOnly").text(prideOnly);

            let trCreator = "";
            for (let i in self.selectedItems) {
                const itemInfo = self.getItemInfo(self.selectedItems[i]);
                if (itemInfo.discountedPrice === "-") {
                    trCreator += `<tr><td class="table-image">${itemInfo.image}</td><td>${itemInfo.id}</td><td>${itemInfo.name}</td><td>${itemInfo.stock}</td><td>${itemInfo.price}</td><td>${itemInfo.discountedPrice}</td><td>${itemInfo.discountRate}</td><td>${itemInfo.saleStart}</td><td>${itemInfo.saleEnd}</td><td>${itemInfo.prideOnly}</td><td>${itemInfo.mcid}</td></tr>`;
                } else {
                    self.selectedItems.slice(Number(i), i);
                }
            }

            $(".index-sale__item-tbody").html(trCreator);

            $(".index-sales__sale1").css("display", "none");
            $(".index-sales__sale2").css("display", "block");
        });

        $("#setSaleConfirm").click(function () {
            const discountRate = $("#discountRate").val();
            const startDate = $("#startDate").val();
            const endDate = $("#endDate").val();
            const prideOnly = $("#prideOnly option:selected").val();

            $("#form-items").val(JSON.stringify(self.selectedItems));
            $("#form-discountRate").val(discountRate);
            $("#form-startDate").val(startDate);
            $("#form-endDate").val(endDate);
            $("#form-prideOnly").val((prideOnly === "プライド限定")?1:0);

            $("#setSaleForm").submit();
        });
        $("#setSalePrev2").click(function () {
            $(".index-sales__sale2").css("display", "none");
            $(".index-sales__sale1").css("display", "block");
        });

        /** セール終了 **/
        $("#endSale").click(function () {
            const ids = self.selectedItems;

            let trCreator = "";
            for (let i in ids) {
                const itemInfo = self.getItemInfo(ids[i]);
                if (itemInfo.discountedPrice !== "-") {
                    trCreator += `<tr><td>${itemInfo.image}</td><td>${itemInfo.id}</td><td>${itemInfo.name}</td><td>${itemInfo.stock}</td><td>${itemInfo.price}</td><td>${itemInfo.discountedPrice}</td><td>${itemInfo.discountRate}</td><td>${itemInfo.saleStart}</td><td>${itemInfo.saleEnd}</td><td>${itemInfo.prideOnly}</td><td>${itemInfo.mcid}</td></tr>`;
                } else {
                    self.selectedItems.slice(i, 1);
                }
            }

            $(".index-sales__confirm-tbody").html(trCreator);

            $(".index-sales__view").css("display", "none");
            $(".index-sales__confirm").css("display", "block");
        });

        $("#endSalePrev").click(function () {
            $(".index-sales__confirm").css("display", "none");
            $(".index-sales__view").css("display", "block");
        });

        $("#endSaleConfirm").click(function () {
            $("#endSaleForm .item").val(JSON.stringify(self.selectedItems));
            $("#endSaleForm").submit()
        });

        /** 販売停止 */
        // 販売停止ボタン
        $("#stop").click(function () {
            const id = self.selectedItems[0];

            const itemInfo = self.getItemInfo(id);
            const trCreator = `<tr><td>${itemInfo.image}</td><td>${itemInfo.id}</td><td>${itemInfo.name}</td><td>${itemInfo.stock}</td><td>${itemInfo.price}</td><td>${itemInfo.discountedPrice}</td><td>${itemInfo.discountRate}</td><td>${itemInfo.saleStart}</td><td>${itemInfo.saleEnd}</td><td>${itemInfo.prideOnly}</td><td>${itemInfo.mcid}</td></tr>`;
            $(".index-sales__confirm-tbody").html(trCreator);

            $(".index-sales__view").css("display", "none");
            $(".index-sales__delete").css("display", "block");
        });

        $("#stopPrev").click(function () {
            $(".index-sales__delete").css("display", "none");
            $(".index-sales__view").css("display", "block");
        });

        $("#stopConfirm").click(function () {
            $("#stopForm .item").val(self.selectedItems[0]);
            $("#stopForm").submit()
        });

        /** 検索バー **/
        $(".tools-form").submit(function (e) {
            e.preventDefault();
            const val = $(".selectbox-3 select option:selected").val();
            self.search($(".tools-form input").val(), val);
        });

        $(".selectbox-3 select").change(function () {
           const val = $(".selectbox-3 select option:selected").val();
           self.search($(".tools-form input").val(), val);
        });
    }

    selectButtons() {
        const self = this;

        /** 選択ボタン */
        // 選択ボタン
        $(".index-sales__button").click(function () {
            $(this).prop("checked", $(this).prop("checked"));
            self.applyButton();
        });

        // 全選択ボタン
        $(".index-sales__all").change(function () {
            const checked = $(this).prop("checked");

            $(".index-sales__button").each(function (index, element) {
                $(element).prop("checked", checked);
            });
            self.applyButton();
        });
    }

    getActive() {
        const self = this;

        $(".index-sales__view-tbody").empty();
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "get/");
        xhr.send();

        xhr.onload = function () {
            self.writeHTML(this.response);
        }
    }


    search(query, sortBy) {
        const self = this;

        $(".index-sales__view-tbody").empty();
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "get/");

        let formData = new FormData();
        formData.append("q", query);
        formData.append("s", sortBy);
        xhr.send(formData);

        xhr.onload = function () {
            self.writeHTML(this.response);
        }
    }

    writeHTML(res) {
        const rs = JSON.parse(res)
        let trCreator = "";
        for (let i in rs) {
            let c = rs[i]

            // checkbox,image,id
            trCreator += `<tr id="${c.id}" class="index-sales__view-tr"><td class="table-checkbox"><input type="checkbox" value="${c.id}" class="index-sales__button"></td><td class="table-image"><img src="${c.image[0]}" alt="商品画像"></td><td class="table-id">${c.id}</td>`;

            // name
            (c.sale_status)?trCreator += `<td class="table-name"><a href="/item/?id=${c.id}" class="is-sale">${c.name}</a></td>`:trCreator += `<td class="table-name"><a href="/item/?id=${c.id}" class>${c.name}</a></td>`;

            // stock,price
            trCreator += `<td class="table-stock">${c.stock}</td><td class="table-price">${this.moneyUnit}${c.price}</td>`;

            // discountprice,discountrate,salestart,endstart,prideonly
            if (c.sale_status) {
                trCreator += `<td class="table-discountedPrice">${this.moneyUnit}${c.discounted_price}</td><td class="table-discountRate">${c.discount_rate}%</td><td class="table-saleStart">${c.sale_start}</td><td class="table-saleEnd">${c.sale_end}</td>`;
                (c.is_pride_only)?trCreator += `<td class="table-prideOnly">プライド限定セール</td>`:trCreator += `<td class="table-prideOnly">通常セール</td>`;
            } else {
                if (c.discount_rate !== null) {
                    trCreator += `<td class="table-discountedPrice">${this.moneyUnit}${c.discounted_price}</td><td class="table-discountRate">${c.discount_rate}%</td><td class="table-saleStart">${c.sale_start}</td><td class="table-saleEnd">${c.sale_end}</td>`;
                    (c.is_pride_only)?trCreator += `<td class="table-prideOnly">プライド限定セール</td>`:trCreator += `<td class="table-prideOnly">通常セール</td>`;
                } else {
                    trCreator += `<td class="table-discountedPrice">-</td><td class="table-discountRate">-</td><td class="table-saleStart">-</td><td class="table-saleEnd">-</td><td class="table-prideOnly">-</td>`;
                }
            }

            // mcid
            trCreator += `<td class="table-mcid">${c.mc_id}</td></tr>`
        }

        $(".index-sales__view-tbody").html(trCreator);
        this.selectButtons();
    }

    getItemInfo(id) {
        const tr = $(`#${id}`);

        const image = tr.find(".table-image").html();
        const name = tr.find(".table-name").text();
        const stock = tr.find(".table-stock").text();
        const price = tr.find(".table-price").text();
        const discountedPrice = tr.find(".table-discountedPrice").text();
        const discountRate = tr.find(".table-discountRate").text();
        const saleStart = tr.find(".table-saleStart").text();
        const saleEnd = tr.find(".table-saleEnd").text();
        const prideOnly = tr.find(".table-prideOnly").text();
        const mcid = tr.find(".table-mcid").text();

        return {
            image: image,
            id: id,
            name: name,
            stock: stock,
            price: price,
            discountedPrice: discountedPrice,
            discountRate: discountRate,
            saleStart: saleStart,
            saleEnd: saleEnd,
            prideOnly: prideOnly,
            mcid: mcid
        }
    }
}

const i = new ItemHandler();
