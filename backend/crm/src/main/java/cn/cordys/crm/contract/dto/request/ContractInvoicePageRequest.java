package cn.cordys.crm.contract.dto.request;

import cn.cordys.common.dto.BasePageRequest;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 发票分页查询入参
 *
 * @author jianxing
 * @date 2025-12-29 18:22:59
 */
@Data
public class ContractInvoicePageRequest extends BasePageRequest {

    @Schema(description = "合同ID")
    private String contractId;

    @Schema(description = "客户ID")
    private String customerId;
}
